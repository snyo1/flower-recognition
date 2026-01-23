from fastapi import APIRouter, HTTPException
from ..models.schemas import QARequest, QAResponse
from ..services.ai import generate_text

router = APIRouter(prefix="/api/qa", tags=["智能问答"])

@router.post("/chat", response_model=QAResponse)
async def chat(request: QARequest):
    try:
        prompt = f"请围绕花卉主题回答：{request.question}"
        ai = generate_text(prompt)
        if ai:
            return QAResponse(answer=ai)
        question = request.question.lower()
        answer = ""
        if '浇水' in question or '水' in question:
            answer = "浇水要根据土壤干湿情况来决定。通常土壤表面干燥时再浇水，浇水要浇透，但要避免积水。夏季需要增加浇水频率，冬季则要减少。不同花卉的需水量不同，建议先了解具体花卉的习性。"
        elif '土壤' in question:
            answer = "大多数花卉喜欢疏松透气、排水良好的土壤。可以使用腐叶土、园土、沙土按2:2:1的比例配制。也可以使用通用花卉营养土，或者根据花卉特性选择专用土壤，如兰花喜欢透气性特别好的松树皮等。"
        elif '病害' in question or '虫' in question:
            answer = "防治病虫害要坚持'预防为主'的原则。保持良好的通风环境，避免过湿，定期检查植株。发现病虫害时，可使用对应的生物农药或低毒化学农药。常见的病虫害有蚜虫、白粉病等，要及时识别并处理。"
        elif '花期' in question:
            answer = "不同花卉的花期不同。春季开花的有郁金香、樱花等；夏季有荷花、向日葵等；秋季有菊花、桂花等；冬季有梅花等。了解花卉的花期有助于更好地安排养护计划。"
        elif '光照' in question or '阳光' in question:
            answer = "大多数花卉需要充足的阳光才能正常开花。但不同花卉对光照的需求不同：喜阳花卉如月季、向日葵需要6小时以上直射光；耐阴花卉如绿萝、龟背竹可在散射光下生长。了解花卉的光照需求，将其放在合适的位置。"
        elif '施肥' in question:
            answer = "施肥要遵循'薄肥勤施'的原则。生长期（春季到秋季）可每月施肥1-2次，冬季休眠期停止施肥。选择合适的肥料类型：观叶植物用氮肥为主的复合肥，观花植物在花期前增加磷钾肥。浓度要稀薄，避免烧伤根系。"
        else:
            answer = f"感谢您的提问！关于'{request.question}'，这是一个很好的问题。关于花卉养护，建议您根据具体的花卉品种来制定养护方案。"
        return QAResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")
