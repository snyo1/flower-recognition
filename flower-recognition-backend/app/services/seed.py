from app.services.db import SessionLocal
from app.models.tables import Flower

def seed_flowers():
    data = [
        {
            "name": "月季",
            "family": "蔷薇科",
            "color": "红色、粉色、黄色等",
            "blooming_period": "5月-10月（夏秋）",
            "description": "月季花被称为\"花中皇后\"，四季开花，花色丰富，芳香浓郁。",
            "care_guide": "喜阳光充足，耐旱耐寒，但不耐水湿。春秋季可每天浇水，保持土壤湿润。生长旺季每月施肥一次。",
            "flower_language": "寓意纯洁的爱、热情和祝福，是爱情的象征。"
        },
        {
            "name": "玫瑰",
            "family": "蔷薇科",
            "color": "红色、粉色、白色等",
            "blooming_period": "5月-10月（夏秋）",
            "description": "玫瑰是世界著名的观赏植物，花形优美，香气浓郁，被称为\"爱情之花\"。",
            "care_guide": "喜温暖、阳光充足的环境，耐寒性较强，需要充足的阳光。春秋季每天浇水，夏季早晚各浇一次。生长季每半月施肥一次。",
            "flower_language": "象征爱情、美丽和热情，表达真挚的情感。"
        },
        {
            "name": "向日葵",
            "family": "菊科",
            "color": "金黄色",
            "blooming_period": "7月-9月（夏季）",
            "description": "向日葵因花序随太阳转动而得名，象征光明和希望。",
            "care_guide": "喜温暖、阳光充足的环境，耐旱不耐涝。每天需6-8小时直射光照。生长期保持土壤微湿，每周浇水一次。",
            "flower_language": "寓意忠诚、爱慕、阳光和希望。"
        },
        {
            "name": "兰花",
            "family": "兰科",
            "color": "白色、紫色、绿色等",
            "blooming_period": "全年（不同品种）",
            "description": "兰花是中国的传统名花，高雅清香，被誉为\"花中君子\"。",
            "care_guide": "喜阴凉湿润环境，忌强光直射。保持空气湿度60%-80%。浇水要见干见湿，避免积水。生长季每月施肥一次薄肥。",
            "flower_language": "象征高洁、典雅、纯洁和友谊。"
        },
        {
            "name": "百合",
            "family": "百合科",
            "color": "白色、粉色、黄色等",
            "blooming_period": "5月-7月（春夏）",
            "description": "百合花姿雅致，清香怡人，寓意百年好合。",
            "care_guide": "喜凉爽、湿润的环境，耐寒怕热。春秋季每2-3天浇水一次，夏季每天浇水。种植前施足基肥，生长期追施磷钾肥。",
            "flower_language": "象征纯洁、高雅、百年好合和美好祝愿。"
        },
        {
            "name": "郁金香",
            "family": "百合科",
            "color": "红色、黄色、粉色、紫色等",
            "blooming_period": "3月-5月（春季）",
            "description": "郁金香是世界著名的球根花卉，花色艳丽，花形优美。",
            "care_guide": "喜凉爽、湿润、阳光充足的环境。春秋季每2-3天浇水一次，夏季休眠期停止浇水。种植前施足基肥，花期前后追施磷钾肥。",
            "flower_language": "象征高贵、典雅、爱情和祝福。"
        }
    ]
    s = SessionLocal()
    try:
        for d in data:
            exists = s.query(Flower).filter(Flower.name == d["name"]).first()
            if exists:
                continue
            row = Flower(
                name=d["name"],
                family=d["family"],
                color=d["color"],
                blooming_period=d["blooming_period"],
                description=d["description"],
                care_guide=d["care_guide"],
                flower_language=d["flower_language"],
            )
            s.add(row)
        s.commit()
    finally:
        s.close()

if __name__ == "__main__":
    seed_flowers()
