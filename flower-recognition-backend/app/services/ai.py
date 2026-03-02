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
    MULTIMODAL_SYSTEM = """你是一个专业的植物学家。分析用户提供的图片，并以 JSON 格式返回识别出的花卉信息。
你必须返回严格的 JSON 格式，不包含任何 Markdown 标记或解释。

JSON 结构如下：
{{
  "name": "花卉名称",
  "family": "科属分类",
  "color": "主要颜色描述",
  "bloomingPeriod": "花期（例如：5月-10月）",
  "description": "详细的植物特征描述，不少于100字",
  "careGuide": "专业的养护方法（包含光照、水分、土壤、施肥、病虫害防治等建议）",
  "flowerLanguage": "花语及其背后的文化内涵或传说",
  "confidence": 95.0
}}"""

    MULTIMODAL_USER = "这张图片中的花卉是什么？请提供详细的科普信息。"

    # 2. 智能问答系统模板
    QA_SYSTEM = """你是一个亲切、专业的花卉科普助手，名字叫“花世界智能管家”。
你擅长解答关于花卉识别、家庭养护、园艺技巧、植物百科、花语寓意等各方面的问题。
你的回答要求：
1. **禁止使用 Markdown 格式**：不要使用星号（*）、井号（#）、反引号（`）等 Markdown 符号。
2. **纯文本分段**：请使用正常的空行来进行分段，使回答清晰易读。
3. 专业且准确：基于植物学事实。
4. 亲切且友好：用通俗易懂的语言，像朋友一样交流。
5. 如果用户的问题与植物或园艺完全无关，请礼貌地告知你只能回答花卉相关的问题。"""

# 核心 AI 逻辑
def generate_text(prompt: str, history: List[Dict[str, str]] = None, system_prompt: Optional[str] = None) -> str:
    """通用文本生成逻辑"""
    if not settings.DEEPSEEK_API_KEY:
        return "DeepSeek API Key 未配置，请联系管理员。"

    try:
        llm = get_llm()
        
        # 构建消息列表
        messages = []
        
        # 系统提示词
        sys_content = system_prompt or PromptTemplates.QA_SYSTEM
        messages.append(SystemMessage(content=sys_content))
        
        # 历史记录
        if history:
            for msg in history:
                role = msg.get("role")
                content = msg.get("content")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
        
        # 当前问题
        messages.append(HumanMessage(content=prompt))
        
        # 调用模型
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        print(f"DeepSeek API Error: {str(e)}")
        return f"抱歉，问答服务暂时不可用 (错误: {str(e)})"

def identify_flower_multimodal(image_bytes: bytes) -> dict:
    """使用 Zhipu AI GLM-4.6V 识别图片中的花卉"""
    if not settings.ZHIPU_API_KEY:
        return {"error": "Zhipu AI API Key 未配置"}

    try:
        # 将图片编码为 base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # 调用 Zhipu AI API
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
            thinking={
                "type": "enabled"
            }
        )
        
        text = response.choices[0].message.content
        
        # 提取并解析 JSON
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            return json.loads(text[start:end])
            
        raise ValueError("AI 未返回有效的 JSON 格式")
    except Exception as e:
        print(f"Zhipu AI Identification Error: {str(e)}")
        return {"error": str(e)}

def generate_flower_info(flower_name: str) -> dict:
    """基于花卉名称生成详细科普信息"""
    try:
        llm = get_llm(temperature=0.7)
        prompt = f"请作为植物学家，为'{flower_name}'生成详细的科普信息。要求包含科属、花期、颜色、详细特征描述、养护指南、花语文化。请以 JSON 格式返回。"
        
        system_msg = SystemMessage(content=PromptTemplates.MULTIMODAL_SYSTEM) # 复用 JSON 结构定义
        
        response = llm.invoke([system_msg, HumanMessage(content=prompt)])
        text = response.content
        
        start = text.find('{')
        end = text.rfind('}') + 1
        return json.loads(text[start:end])
    except Exception as e:
        print(f"Generate Info Error: {str(e)}")
        return {}
