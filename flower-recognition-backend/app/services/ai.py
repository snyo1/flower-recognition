from typing import List, Dict, Any, Optional
import json
import base64
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from ..core.config import settings

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
    # 1. 花卉识别与科普信息生成模板
    IDENTIFICATION_SYSTEM = """你是一个专业的花卉专家和植物学家。
你的任务是根据用户提供的花卉名称或描述，生成详细的科普信息。
你必须以严格的 JSON 格式返回结果，不包含任何解释性文字或 Markdown 代码块标记。

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

    IDENTIFICATION_USER = "请为以下花卉生成科普信息：{flower_info}"

    # 2. 智能问答系统模板
    QA_SYSTEM = """你是一个亲切、专业的花卉科普助手，名字叫“花世界智能管家”。
你擅长解答关于花卉识别、家庭养护、园艺技巧、植物百科、花语寓意等各方面的问题。
你的回答应该：
1. 专业且准确：基于植物学事实。
2. 亲切且友好：用通俗易懂的语言，像朋友一样交流。
3. 结构清晰：如果回答较长，请使用分点说明。
4. 引导性：如果用户提问模糊，可以尝试引导其提供更多细节（如叶片形状、生长环境等）。

如果用户的问题与植物或园艺完全无关，请礼貌地告知你只能回答花卉相关的问题。"""

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

def identify_and_generate(image_data: bytes = None, image_hint: str = "未知花卉") -> dict:
    """
    识别花卉并生成科普信息。
    注意：由于 DeepSeek 主要是文本模型，目前流程为：
    1. 前端/后端通过其他方式初步确定名称（或 image_hint 为识别出的名称）
    2. 使用 DeepSeek 生成高质量的科普内容。
    """
    if not settings.DEEPSEEK_API_KEY:
        # 离线兜底
        return {
            "name": image_hint,
            "family": "未知",
            "color": "未知",
            "bloomingPeriod": "未知",
            "description": "DeepSeek API 未配置，无法生成详细科普内容。",
            "careGuide": "暂无养护建议。",
            "flowerLanguage": "暂无花语信息。",
            "confidence": 0.0
        }

    try:
        llm = get_llm(temperature=0.2, timeout=45) # 识别任务降低随机性，并稍微缩短超时以快速反馈
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", PromptTemplates.IDENTIFICATION_SYSTEM),
            ("human", PromptTemplates.IDENTIFICATION_USER)
        ])
        
        chain = prompt_template | llm
        
        response = chain.invoke({"flower_info": image_hint})
        text = response.content
        
        # 提取并解析 JSON
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = text[start:end]
            return json.loads(json_str)
            
        raise ValueError("AI 未返回有效的 JSON 格式")
        
    except Exception as e:
        print(f"Identification Error: {str(e)}")
        return {
            "name": image_hint,
            "family": "处理中",
            "color": "见图",
            "bloomingPeriod": "咨询中",
            "description": f"获取科普信息失败: {str(e)}",
            "careGuide": "请稍后再试",
            "flowerLanguage": "未知",
            "confidence": 0.0
        }
