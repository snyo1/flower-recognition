from typing import List, Dict, Any, Optional
import json
import base64
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
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
        max_tokens=800,
    )

class PromptTemplates:
    MULTIMODAL_SYSTEM = (
        '你是一个世界级的植物学专家和园艺大师。你的任务是分析用户上传的花卉图片。\n'
        '你的分析必须极其专业、准确，并且能够识别出甚至是罕见或小众的品种。\n\n'
        '请按照以下 JSON 结构返回结果，不要包含任何 Markdown 代码块标记或任何额外的文字说明。\n\n'
        '{{\n'
        '  "name": "花卉名称 (如果品种罕见，请给出精确的学术名称)",\n'
        '  "family": "精确的科属分类 (例如：蔷薇科 蔷薇属)",\n'
        '  "color": "详细的颜色描述 (包括渐变、斑点等细节)",\n'
        '  "bloomingPeriod": "花期（例如：5月-10月，如果是温室栽培请注明）",\n'
        '  "description": "详尽的植物特征描述，不少于200字。包括叶片形状、花瓣质感、生长习性等。",\n'
        '  "careGuide": "专业的养护指南。涵盖光照、浇水、土壤、施肥、病虫害防治。",\n'
        '  "flowerLanguage": "花语寓意、历史背景、文化内涵或相关传说。",\n'
        '  "confidence": 你对识别结果的置信度(0到100的浮点数)。根据图片清晰度和花卉特征可辨识程度客观评估。图片模糊或特征不明显应低于80，特征明确且有把握可给90以上。,\n'
        '  "type": "草本/木本/多肉/藤本"\n'
        '}}'
    )

    MULTIMODAL_USER = "请识别这张图片中的植物，并提供最专业的百科知识。"

    QA_SYSTEM = (
        '你是一个亲切、博学且专业的花卉科普助手，名字叫花世界智能管家。\n'
        '你拥有深厚的植物学背景和丰富的家庭园艺实践经验。\n\n'
        '你的职责：\n'
        '1. 识别与诊断：基于描述识别植物，诊断生长问题。\n'
        '2. 养护指导：提供浇水、施肥、修剪建议。\n'
        '3. 文化科普：分享花语、文化意义和植物故事。\n\n'
        '回答准则：\n'
        '1. 使用纯文本格式，严禁使用Markdown标记（禁止星号、井号、反引号、短横线列表等）。\n'
        '2. 用数字编号代替列表，用换行分段。\n'
        '3. 回答简洁精炼，控制在300字以内。\n'
        '4. 养护问题要解释原因。\n'
        '5. 根据用户环境给适配建议。\n'
        '6. 非花卉问题礼貌引导回主题。'
    )

def _robust_json_parse(text: str) -> dict:
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find('{')
    end = text.rfind('}') + 1
    if start == -1 or end == 0:
        raise ValueError(f"未能从返回内容中找到 JSON 结构: {text[:100]}...")
    json_str = text[start:end]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON 解析初次失败，尝试修复: {str(e)}")
        raise e

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
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        response = zhipu_client.chat.completions.create(
            model=settings.ZHIPU_MODEL,
            messages=[
                {"role": "system", "content": PromptTemplates.MULTIMODAL_SYSTEM},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                        {"type": "text", "text": PromptTemplates.MULTIMODAL_USER},
                    ],
                },
            ],
        )
        text = response.choices[0].message.content
        return _robust_json_parse(text)
    except Exception as e:
        print(f"多模态识别失败: {str(e)}")
        return {"error": f"识别引擎响应异常: {str(e)}"}

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
