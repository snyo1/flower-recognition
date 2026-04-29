from typing import List, Dict, Any, Optional
import io
import json
import base64
import re
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from ..core.config import settings
from zai import ZhipuAiClient

zhipu_client = ZhipuAiClient(api_key=settings.ZHIPU_API_KEY)

def get_llm(model: str = "deepseek-chat", temperature: float = 0.7, timeout: int = 30):
    return ChatOpenAI(
        model=model,
        openai_api_key=settings.DEEPSEEK_API_KEY,
        openai_api_base=settings.DEEPSEEK_BASE_URL + "/v1",
        temperature=temperature,
        timeout=timeout,
        max_retries=1,
        max_tokens=520,
    )

class PromptTemplates:
    MULTIMODAL_SYSTEM = (
        '你是一名花卉识别助手，请优先快速、客观地识别图片中的花卉，并返回简洁 JSON。\n'
        '如果无法确定具体品种，可返回较稳妥的常见名称，不要虚构。\n'
        '描述要短，减少生成耗时；置信度必须真实反映把握度，严禁固定给高分。\n\n'
        '仅返回 JSON，不要输出 Markdown 或解释。\n\n'
        '{{\n'
        '  "name": "花卉名称，无法确认时写未识别",\n'
        '  "family": "科属或常见分类，未知可写未知",\n'
        '  "color": "1-2个主要颜色",\n'
        '  "bloomingPeriod": "常见花期，未知可写未知",\n'
        '  "description": "50字以内，概括花朵外观特征",\n'
        '  "careGuide": "50字以内，给出最核心养护建议",\n'
        '  "flowerLanguage": "30字以内，可简述花语或写暂无",\n'
        '  "confidence": 0到100的数字,\n'
        '  "type": "草本/木本/多肉/藤本/未知"\n'
        '}}\n\n'
        '置信度规则：\n'
        '1. 图片模糊、遮挡、多花混杂：25-55。\n'
        '2. 只看出大类，不能确认品种：56-74。\n'
        '3. 主要特征明显，但仍存在相似品种：75-88。\n'
        '4. 特征非常清晰且高度确定：89-96。\n'
        '5. 除非证据极强，不要超过96；不要总是返回95。'
    )

    MULTIMODAL_USER = '请在保证准确性的前提下，尽快识别这张花卉图片并返回精简结果。'

    QA_SYSTEM = (
        '你是花世界智能管家，一名专业、耐心、审美在线的花卉问答助手。\n'
        '你擅长家庭养花、校园常见花木识别、病虫害初步判断、送花场景建议与花语科普。\n\n'
        '回答目标：在不拖慢响应的前提下，让答案清晰、实用、好读。\n\n'
        '回答要求：\n'
        '1. 使用简洁 Markdown，让前端更易展示。\n'
        '2. 优先使用以下结构中的合适部分，而不是每次都全部输出：\n'
        '   标题一行；\n'
        '   1个简短结论段；\n'
        '   3-5条要点列表；\n'
        '   1条提醒或避坑建议。\n'
        '3. 总长度尽量控制在220字以内，复杂问题最多不超过320字。\n'
        '4. 养护建议必须具体，可直接执行，尽量包含频率、光照、浇水或土壤关键点。\n'
        '5. 遇到病害、黄叶、烂根等问题，要先给最可能原因，再给处理步骤。\n'
        '6. 不确定时要明确说明“可能”“更像”，不要编造。\n'
        '7. 非花卉相关问题，礼貌简短地引导回花卉主题。\n'
        '8. 不要写长篇空话，不要重复用户问题，不要输出代码块。'
    )

def _robust_json_parse(text: str) -> dict:
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find('{')
    if start == -1:
        raise ValueError(f"未能从返回内容中找到 JSON 结构: {text[:100]}...")

    json_candidate = text[start:]
    end = json_candidate.rfind('}')
    if end != -1:
        json_candidate = json_candidate[:end + 1]

    try:
        return json.loads(json_candidate)
    except json.JSONDecodeError as e:
        repaired = _repair_truncated_json(json_candidate)
        if repaired:
            return repaired
        print(f"JSON 解析失败，原始片段: {json_candidate[:200]}...")
        raise ValueError(f"未能从返回内容中恢复 JSON 结构: {json_candidate[:100]}...") from e


def _repair_truncated_json(text: str) -> dict | None:
    result: dict[str, Any] = {}
    field_patterns = {
        "name": r'"name"\s*:\s*"([^"\n\r]*)',
        "family": r'"family"\s*:\s*"([^"\n\r]*)',
        "color": r'"color"\s*:\s*"([^"\n\r]*)',
        "bloomingPeriod": r'"bloomingPeriod"\s*:\s*"([^"\n\r]*)',
        "description": r'"description"\s*:\s*"([^"\n\r]*)',
        "careGuide": r'"careGuide"\s*:\s*"([^"\n\r]*)',
        "flowerLanguage": r'"flowerLanguage"\s*:\s*"([^"\n\r]*)',
        "type": r'"type"\s*:\s*"([^"\n\r]*)',
    }

    for field, pattern in field_patterns.items():
        match = re.search(pattern, text, re.S)
        if match:
            value = match.group(1).strip().strip(',，。；;')
            if value:
                result[field] = value

    confidence_match = re.search(r'"confidence"\s*:\s*([0-9]+(?:\.[0-9]+)?)', text)
    if confidence_match:
        result["confidence"] = float(confidence_match.group(1))

    if result.get("name"):
        result.setdefault("family", "未知")
        result.setdefault("color", "未知")
        result.setdefault("bloomingPeriod", "未知")
        result.setdefault("description", "可见部分花卉特征。")
        result.setdefault("careGuide", "保持通风和适度光照。")
        result.setdefault("flowerLanguage", "暂无")
        result.setdefault("type", "未知")
        result.setdefault("confidence", 68.0)
        return result
    return None


def _normalize_confidence_value(value: Any, default: float = 72.0) -> float:
    if isinstance(value, (int, float)):
        confidence = float(value)
    elif isinstance(value, str):
        try:
            confidence = float(value.strip().replace('%', ''))
        except ValueError:
            confidence = default
    else:
        confidence = default
    return max(0.0, min(100.0, confidence))


def _post_process_result(result: dict) -> dict:
    def clean_text(value: Any, fallback: str) -> str:
        text = str(value or '').strip().strip(',，。；;')
        if not text:
            return fallback
        if text.endswith((':', '：', '"', "'")):
            return fallback
        return text

    result['name'] = clean_text(result.get('name'), '未识别')
    result['family'] = clean_text(result.get('family'), '未知')
    result['color'] = clean_text(result.get('color'), '未知')
    result['bloomingPeriod'] = clean_text(result.get('bloomingPeriod'), '未知')
    result['description'] = clean_text(result.get('description'), '可见典型花部特征。')
    result['careGuide'] = clean_text(result.get('careGuide'), '保持通风和适度光照。')
    result['flowerLanguage'] = clean_text(result.get('flowerLanguage'), '暂无')
    result['type'] = clean_text(result.get('type'), '未知')
    result['confidence'] = round(_normalize_confidence_value(result.get('confidence', 70.0)), 1)
    return result


def _call_multimodal_api(image_base64: str, prompt_text: str, max_tokens: int = 320, timeout: int = 8) -> dict:
    response = zhipu_client.chat.completions.create(
        model=settings.ZHIPU_MODEL,
        temperature=0.08,
        max_tokens=max_tokens,
        timeout=timeout,
        messages=[
            {"role": "system", "content": PromptTemplates.MULTIMODAL_SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                    {"type": "text", "text": prompt_text},
                ],
            },
        ],
    )
    return _robust_json_parse(response.choices[0].message.content)


def _encode_image(image: Image.Image, max_side: int = 768, quality: int = 76) -> str:
    copied = image.copy()
    copied.thumbnail((max_side, max_side))
    buffer = io.BytesIO()
    copied.save(buffer, format="JPEG", quality=quality, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def generate_text(prompt: str, history: List[Dict[str, str]] = None, system_prompt: Optional[str] = None) -> str:
    if not settings.DEEPSEEK_API_KEY:
        return "DeepSeek API Key 未配置，请联系管理员。"
    try:
        temp = 0.3 if any(k in prompt for k in ["怎么养", "养护", "病", "死", "土", "水"]) else 0.7
        llm = get_llm(temperature=temp)
        messages = []
        sys_content = system_prompt or PromptTemplates.QA_SYSTEM
        messages.append(SystemMessage(content=sys_content))

        if history:
            window_history = history[-6:]
            for msg in window_history:
                role = msg.get("role")
                content = msg.get("content")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))

        messages.append(HumanMessage(content=prompt))
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        print(f"AI 生成错误: {str(e)}")
        return f"抱歉，智能管家遇到了一点技术问题，请稍后再试。({str(e)})"

def identify_flower_multimodal(image_bytes: bytes) -> dict:
    if not settings.ZHIPU_API_KEY:
        return {"error": "Zhipu AI API Key 未配置"}
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_base64 = _encode_image(image, max_side=768, quality=78)
        result = _call_multimodal_api(image_base64, PromptTemplates.MULTIMODAL_USER, max_tokens=320, timeout=8)
        result = _post_process_result(result)
        if result.get("name") in {"未识别", "未知", "不确定", "无法识别"}:
            fallback_result = identify_flower_multimodal_fallback(image_bytes)
            if "error" not in fallback_result:
                return _post_process_result(fallback_result)
        return result
    except Exception as e:
        print(f"多模态识别失败: {str(e)}")
        fallback_result = identify_flower_multimodal_fallback(image_bytes)
        if "error" not in fallback_result:
            return _post_process_result(fallback_result)
        return {"error": f"识别引擎响应异常: {str(e)}"}


def identify_flower_multimodal_fallback(image_bytes: bytes) -> dict:
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        fallback_base64 = _encode_image(image, max_side=640, quality=72)
        prompt = '请基于缩略图再次识别，优先给出最可能的常见花名；若只能判断到大类，也请返回较稳妥结果。'
        return _call_multimodal_api(fallback_base64, prompt, max_tokens=260, timeout=8)
    except Exception as e:
        print(f"多模态兜底识别失败: {str(e)}")
        return {"error": f"兜底识别失败: {str(e)}"}


def generate_flower_info(flower_name: str) -> dict:
    try:
        llm = get_llm(temperature=0.4)
        prompt = f"请作为植物学家，为'{flower_name}'生成百科科普信息。包含科属分类、特征描述、养护指南、花语文化。严格按JSON格式返回。"
        system_msg = SystemMessage(content=PromptTemplates.MULTIMODAL_SYSTEM)
        response = llm.invoke([system_msg, HumanMessage(content=prompt)])
        return _robust_json_parse(response.content)
    except Exception as e:
        print(f"生成百科信息失败: {str(e)}")
        return {"name": flower_name, "description": "暂无详细资料"}
