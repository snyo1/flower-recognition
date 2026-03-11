from typing import List, Dict, Any, Optional
import json
import base64
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from ..core.config import settings
from zai import ZhipuAiClient

# 初始化 Zhipu AI 客户端
zhipu_client = ZhipuAiClient(api_key=settings.ZHIPU_API_KEY)

# 初始化 DeepSeek 模型 (使用 langchain-openai 的适配器)
def get_llm(model: str = "deepseek-chat", temperature: float = 0.7, timeout: int = 60):
    return ChatOpenAI(
        model=model,
        openai_api_key=settings.DEEPSEEK_API_KEY,
        openai_api_base=settings.DEEPSEEK_BASE_URL + "/v1", # 注意补全 /v1
        temperature=temperature,
        timeout=timeout,
        max_retries=2
    )

# 提示词模板定义
class PromptTemplates:
    # 1. 多模态花卉识别模板
    MULTIMODAL_SYSTEM = """你是一个世界级的植物学专家和园艺大师。你的任务是分析用户上传的花卉图片。
你的分析必须极其专业、准确，并且能够识别出甚至是罕见或小众的品种。

请按照以下 JSON 结构返回结果，不要包含任何 Markdown 代码块标记（如 ```json）或任何额外的文字说明。

{{
  "name": "花卉名称 (如果品种罕见，请给出精确的学术名称)",
  "family": "精确的科属分类 (例如：蔷薇科 蔷薇属)",
  "color": "详细的颜色描述 (包括渐变、斑点等细节)",
  "bloomingPeriod": "花期（例如：5月-10月，如果是温室栽培请注明）",
  "description": "极其详尽的植物特征描述，不少于200字。包括叶片形状、花瓣质感、生长习性等。",
  "careGuide": "专业的养护指南。必须涵盖：1.光照要求；2.灌溉频率与技巧；3.土壤成分建议；4.施肥周期；5.常见病虫害及防治方案。",
  "flowerLanguage": "深度的花语寓意、历史背景、文化内涵或相关传说。",
  "confidence": 95.0,
  "type": "草本/木本/多肉/藤本"
}}"""

    MULTIMODAL_USER = "请识别这张图片中的植物，并提供最专业的百科知识。"

    # 2. 智能问答系统模板
    QA_SYSTEM = """你是一个亲切、博学且专业的花卉科普助手，名字叫“花世界智能管家”。
你拥有深厚的植物学背景和丰富的家庭园艺实践经验。

你的职责：
1. 识别与诊断：基于描述或历史图片识别植物，并诊断可能的生长问题。
2. 养护指导：提供量身定制的浇水、施肥、修剪建议。
3. 文化科普：分享花语、文化意义和植物背后的故事。

回答准则：
- **格式控制**：严禁使用 Markdown 标记（如 *、#、`）。使用纯文本并用双换行符进行清晰的分段。
- **专业深度**：不要只给表面答案。如果是关于养护的问题，请解释“为什么”要这样做。
- **场景感知**：根据用户提到的环境（如“办公室”、“南阳台”）给出适配的建议。
- **边界清晰**：如果问题与植物、园艺、大自然完全无关，请礼貌地引导用户回到花卉话题。"""

def _robust_json_parse(text: str) -> dict:
    """鲁棒的 JSON 解析器，处理 AI 返回的各种格式"""
    # 移除 Markdown 代码块标记
    text = text.replace("```json", "").replace("```", "").strip()
    
    # 寻找第一个 { 和最后一个 }
    start = text.find('{')
    end = text.rfind('}') + 1
    
    if start == -1 or end == 0:
        raise ValueError(f"未能从返回内容中找到 JSON 结构: {text[:100]}...")
        
    json_str = text[start:end]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # 尝试修复常见的 JSON 错误（如末尾多余的逗号）
        # 简单的正则或字符串处理可以在这里增加
        print(f"JSON 解析初次失败，尝试修复: {str(e)}")
        # 这里可以加入更复杂的修复逻辑，目前先抛出
        raise e

# 核心 AI 逻辑
def generate_text(prompt: str, history: List[Dict[str, str]] = None, system_prompt: Optional[str] = None) -> str:
    """增强的文本生成逻辑，支持上下文窗口管理"""
    if not settings.DEEPSEEK_API_KEY:
        return "DeepSeek API Key 未配置，请联系管理员。"

    try:
        # 动态调整 temperature: 养护建议需要准确(低)，文化花语可以有创意(高)
        temp = 0.3 if any(k in prompt for k in ["怎么养", "养护", "病", "死", "土", "水"]) else 0.7
        llm = get_llm(temperature=temp)
        
        messages = []
        
        # 1. 系统提示词
        sys_content = system_prompt or PromptTemplates.QA_SYSTEM
        messages.append(SystemMessage(content=sys_content))
        
        # 2. 上下文滑动窗口：仅保留最近 6 轮对话，避免冗余和超出 Token 限制
        if history:
            window_history = history[-12:] # 6对问答
            for msg in window_history:
                role = msg.get("role")
                content = msg.get("content")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
        
        # 3. 当前问题增强：如果历史中提到了特定花卉，将其注入当前 context
        enhanced_prompt = prompt
        messages.append(HumanMessage(content=enhanced_prompt))
        
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        print(f"AI 生成错误: {str(e)}")
        return f"抱歉，智能管家遇到了一点技术问题，请稍后再试。({str(e)})"

def identify_flower_multimodal(image_bytes: bytes) -> dict:
    """使用 Zhipu AI GLM-4.6V 识别图片中的花卉，增强鲁棒性"""
    if not settings.ZHIPU_API_KEY:
        return {"error": "Zhipu AI API Key 未配置"}

    try:
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        response = zhipu_client.chat.completions.create(
            model=settings.ZHIPU_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": PromptTemplates.MULTIMODAL_SYSTEM
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": PromptTemplates.MULTIMODAL_USER
                        }
                    ]
                }
            ],
            thinking={"type": "enabled"}
        )
        
        text = response.choices[0].message.content
        return _robust_json_parse(text)
        
    except Exception as e:
        print(f"多模态识别失败: {str(e)}")
        return {"error": f"识别引擎响应异常: {str(e)}"}

def generate_flower_info(flower_name: str) -> dict:
    """基于花卉名称生成详细科普信息，使用增强的 JSON 解析"""
    try:
        llm = get_llm(temperature=0.4) # 科普信息需要相对稳健
        prompt = f"请作为植物学家，为'{flower_name}'生成最专业的百科科普信息。必须包含科属分类、详细特征描述、分步骤养护指南、深度花语文化内涵。请严格按要求的 JSON 格式返回。"
        
        system_msg = SystemMessage(content=PromptTemplates.MULTIMODAL_SYSTEM)
        
        response = llm.invoke([system_msg, HumanMessage(content=prompt)])
        return _robust_json_parse(response.content)
    except Exception as e:
        print(f"生成百科信息失败: {str(e)}")
        return {"name": flower_name, "description": "暂无详细资料"}
