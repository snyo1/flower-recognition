import os
import requests
import json
import base64
from typing import List, Dict, Any

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# 提示词模板
PROMPT_TEMPLATES = {
    "identification": """你是一个专业的花卉专家。请分析上传的花卉图片（或描述），并以JSON格式返回以下信息：
{
  "name": "花卉名称",
  "family": "科属分类",
  "color": "主要颜色",
  "bloomingPeriod": "花期（如5月-10月）",
  "description": "详细的特征描述",
  "careGuide": "专业的养护方法（包含生长习性、浇水、施肥、病虫害防治）",
  "flowerLanguage": "花语和文化内涵",
  "confidence": 95.0
}
请确保JSON格式正确，不要包含任何其他文字。""",
    
    "qa": "你是一个花卉科普助手。请根据用户的提问提供专业、友好的回答。如果涉及图片，请结合图片内容回答。"
}

def generate_text(prompt: str, history: List[Dict[str, str]] = None, system_prompt: str = None) -> str:
    if not DEEPSEEK_API_KEY:
        # 离线模拟逻辑
        if "识别" in prompt or "图片" in prompt:
            return json.dumps({
                "name": "郁金香",
                "family": "百合科",
                "color": "红色、紫色、黄色",
                "bloomingPeriod": "3月-5月",
                "description": "郁金香被誉为'世界花后'，花朵单生茎顶，大而艳丽。",
                "careGuide": "喜凉爽，耐寒。浇水见干见湿，生长期追施复合肥。",
                "flowerLanguage": "博爱、体贴、高雅、富贵、能干、聪颖。",
                "confidence": 98.0
            }, ensure_ascii=False)
        return "我是花卉识别系统，目前处于离线模式。请检查API密钥配置。"

    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": PROMPT_TEMPLATES["qa"]})
            
        if history:
            messages.extend(history)
            
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": DEEPSEEK_MODEL,
            "messages": messages,
            "temperature": 0.7,
        }
        resp = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content or ""
    except Exception as e:
        print(f"AI API Error: {str(e)}")
        return ""

def identify_and_generate(image_data: bytes = None, image_hint: str = "花卉图片") -> dict:
    # 如果有图片数据，这里应该是多模态调用。
    # 由于DeepSeek目前主模型多为文本，我们假设通过描述或多模态接口。
    # 如果是多模态，payload会有所不同（如包含base64图片）。
    
    prompt = f"识别这朵花：{image_hint}"
    if image_data:
        # 模拟多模态处理：如果是真正支持多模态的API，会在这里处理base64
        # base64_image = base64.b64encode(image_data).decode('utf-8')
        pass

    text = generate_text(prompt, system_prompt=PROMPT_TEMPLATES["identification"])
    
    try:
        # 尝试提取JSON
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = text[start:end]
            result = json.loads(json_str)
            return result
    except Exception:
        pass

    # 兜底返回
    return {
        "name": "未知花卉",
        "family": "未知科属",
        "color": "未知",
        "bloomingPeriod": "全年",
        "description": text if text else "无法识别该图片",
        "careGuide": "保持通风光照，见干见湿浇水。",
        "flowerLanguage": "自然之美。",
        "confidence": 50.0,
    }
