import os
import requests

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "AI取名")

def generate_text(prompt: str) -> str:
    if not DEEPSEEK_API_KEY:
        return ""
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": "你是花卉识别与科普助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }
        resp = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content or ""
    except Exception:
        return ""

def identify_and_generate(image_hint: str) -> dict:
    text = generate_text(f"请根据提示识别花卉并生成名称、科属、颜色、花期、特征描述、养护方法、花语，并给出识别置信度。提示：{image_hint}")
    if not text:
        return {}
    name = ""
    family = ""
    color = ""
    blooming_period = ""
    description = ""
    care_guide = ""
    flower_language = ""
    confidence = 90.0
    return {
        "name": name or "未知花卉",
        "family": family or "未知科属",
        "color": color or "未知",
        "bloomingPeriod": blooming_period or "全年",
        "description": description or text,
        "careGuide": care_guide or "保持通风光照，见干见湿浇水，薄肥勤施。",
        "flowerLanguage": flower_language or "美好与祝福。",
        "confidence": confidence,
    }
