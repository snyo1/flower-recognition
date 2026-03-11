import asyncio
import sys
import os

# 将项目根目录添加到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.db import engine, AsyncSessionFactory
from app.models.tables import Flower, Base
from sqlalchemy import select, text

flowers_data = [
    {
        "name": "月季", "family": "蔷薇科 蔷薇属", "color": "红、粉、黄、白、橙", "blooming_period": "4月-11月",
        "description": "月季花被称为'花中皇后'，品种繁多，花色丰富。其叶片平滑，边缘有锯齿，茎部通常带有皮刺。",
        "care_guide": "1.光照：需充足阳光，每天至少6小时；2.水分：见干见湿，避免积水；3.土壤：疏松肥沃的微酸性土；4.施肥：生长期每10天施一次薄肥；5.修剪：花后及时剪除残花。",
        "flower_language": "持之以恒、等待希望、美艳与高贵。", "plant_type": "木本"
    },
    {
        "name": "牡丹", "family": "芍药科 芍药属", "color": "红、紫、粉、白、黄", "blooming_period": "4月-5月",
        "description": "牡丹是中国传统名花，有'国色天香'之称。花朵硕大，花瓣重叠，气派非凡。",
        "care_guide": "1.光照：喜光但忌暴晒，夏季需遮阴；2.水分：耐旱怕涝，保持盆土微湿即可；3.土壤：深厚、肥沃、排水良好的砂质土；4.施肥：春秋季各施肥一次；5.温度：耐寒不耐高温。",
        "flower_language": "圆满、浓情、富贵、端庄、仪态万千。", "plant_type": "木本"
    },
    {
        "name": "向日葵", "family": "菊科 向日葵属", "color": "金黄色", "blooming_period": "7月-9月",
        "description": "一年生草本植物，花盘随太阳转动。茎直立粗壮，被白色粗硬毛。",
        "care_guide": "1.光照：必须全日照，光照不足会导致花盘细小；2.水分：生长期需水量大，需保持土壤湿润；3.土壤：对土壤要求不严，排水良好即可；4.施肥：需氮磷钾均衡肥；5.支撑：植株较高时需设立支柱。",
        "flower_language": "沉默的爱、爱慕、忠诚、阳光、希望。", "plant_type": "草本"
    },
    {
        "name": "兰花", "family": "兰科 兰属", "color": "绿、黄、白、红、紫", "blooming_period": "冬春季（春兰）、夏季（建兰）",
        "description": "中国传统名花，被誉为'花中君子'。叶片修长，花姿幽雅，香气清远。",
        "care_guide": "1.光照：喜半阴，忌强光直射；2.水分：喜湿润但忌积水，建议喷雾增加湿度；3.土壤：专用的兰花土（如松皮、植金石）；4.施肥：施专用兰肥，忌浓肥；5.通风：需空气流通良好的环境。",
        "flower_language": "高洁、典雅、爱国、坚贞不渝、贤德。", "plant_type": "草本"
    },
    {
        "name": "郁金香", "family": "百合科 郁金香属", "color": "红、黄、紫、白、粉", "blooming_period": "3月-5月",
        "description": "世界著名的球根花卉。花朵单生茎顶，杯状，色彩艳丽，具有丝绸般的光泽。",
        "care_guide": "1.光照：喜阳光，每天需8小时以上光照；2.水分：保持土壤湿润，不可积水；3.土壤：疏松、肥沃、排水良好的微酸性砂质壤土；4.温度：喜凉爽干燥环境，耐寒性强；5.花后处理：花谢后剪掉残花，保留叶片养球。",
        "flower_language": "博爱、体贴、高雅、富贵、能干、聪颖。", "plant_type": "草本"
    },
    {
        "name": "茉莉花", "family": "木犀科 素馨属", "color": "纯白色", "blooming_period": "5月-8月",
        "description": "常绿灌木，花朵洁白无瑕，香味浓郁悠长，是重要的香料植物。",
        "care_guide": "1.光照：喜强光，有'晒不死的茉莉'之说；2.水分：喜湿润，夏季早晚各浇水一次；3.土壤：富含腐殖质的微酸性土壤；4.施肥：生长期需多施磷钾肥；5.修剪：花后重剪以促萌发新枝。",
        "flower_language": "忠贞、清纯、贞洁、质朴、玲珑、迷人。", "plant_type": "木本"
    },
    {
        "name": "绣球花", "family": "绣球花科 绣球属", "color": "蓝、粉、紫、白（受酸碱度影响）", "blooming_period": "6月-8月",
        "description": "花型丰满，大而美丽，花色能随土壤酸碱度变化。酸蓝碱粉。",
        "care_guide": "1.光照：喜半阴环境，忌烈日暴晒；2.水分：极度喜水，需保持土壤湿润；3.土壤：疏松肥沃排水好的土壤；4.调色：施硫酸铝可变蓝，施石灰可变粉；5.施肥：生长期每半月施一次复合肥。",
        "flower_language": "希望、健康、有耐性的爱情、美满、团圆。", "plant_type": "木本"
    },
    {
        "name": "栀子花", "family": "茜草科 栀子属", "color": "白色", "blooming_period": "5月-7月",
        "description": "常绿灌木，花朵洁白，芳香四溢。叶片翠绿有光泽。",
        "care_guide": "1.光照：喜充足阳光，但夏季需适当遮阴；2.水分：喜湿润环境，经常喷水增加空气湿度；3.土壤：必须是酸性土壤，否则易得失绿病；4.施肥：生长期施矾肥水（酸性肥）；5.温度：喜温暖，北方需室内越冬。",
        "flower_language": "喜悦、永恒的爱、一生的守候、清净。", "plant_type": "木本"
    },
    {
        "name": "百合花", "family": "百合科 百合属", "color": "白、粉、黄、橙、红", "blooming_period": "5月-7月",
        "description": "球根花卉，花姿雅致，叶片青翠，茎干亭亭玉立。百合寓意'百年好合'。",
        "care_guide": "1.光照：喜柔和光照，忌强光直射根部；2.水分：见干见湿，切忌水涝导致种球腐烂；3.土壤：富含腐殖质、排水良好的砂质土；4.施肥：生长期追施磷钾肥；5.环境：喜凉爽，不耐高温。",
        "flower_language": "百年好合、美好家庭、伟大的爱、深深的祝福。", "plant_type": "草本"
    },
    {
        "name": "康乃馨", "family": "石竹科 石竹属", "color": "红、粉、黄、白", "blooming_period": "4月-9月",
        "description": "多年生草本，是母亲节的象征。花瓣边缘有锯齿，带有淡淡的香气。",
        "care_guide": "1.光照：喜光，全日照环境下开花更好；2.水分：耐旱不耐潮湿，保持盆土微干；3.土壤：排水良好的石灰质土壤；4.施肥：每半月施一次稀薄液肥；5.摘心：幼苗期需多次摘心以促进分枝。",
        "flower_language": "母亲我爱您、热情、真纯的爱、慈祥、宽容。", "plant_type": "草本"
    },
    {
        "name": "薰衣草", "family": "唇形科 薰衣草属", "color": "紫色、蓝紫色", "blooming_period": "6月-8月",
        "description": "半灌木或矮灌木，著名的香草植物。叶片线形，花序呈穗状。",
        "care_guide": "1.光照：全日照，阳光不足会导致植株衰弱；2.水分：耐旱，保持土壤微干，切忌积水；3.土壤：排水良好的石灰质土；4.施肥：对肥料要求不高，每年施一次底肥即可；5.修剪：定期修剪以保持株型并防止木质化。",
        "flower_language": "等待爱情、只要用力呼吸就能看见奇迹。", "plant_type": "木本"
    },
    {
        "name": "太阳花", "family": "马齿苋科 马齿苋属", "color": "红、橙、黄、白、粉", "blooming_period": "5月-11月",
        "description": "又名半支莲、大花马齿苋。见阳光开花，早、晚、阴天闭合。",
        "care_guide": "1.光照：极度喜光，阳光越强开花越旺；2.水分：极度耐旱，半月不浇水也不会死；3.土壤：排水良好的砂质土；4.繁殖：插条极易成活；5.施肥：每月施一次稀薄氮肥。",
        "flower_language": "沉默的爱、光明、热烈、忠诚、勇敢、自强不息。", "plant_type": "草本"
    },
    {
        "name": "菊花", "family": "菊科 菊属", "color": "黄、白、红、紫、绿", "blooming_period": "9月-11月",
        "description": "中国十大名花之一，'梅兰竹菊'四君子之一。耐寒，傲霜怒放。",
        "care_guide": "1.光照：短日照植物，每天光照不宜超过10小时；2.水分：喜湿润但忌涝；3.土壤：疏松肥沃的砂质壤土；4.施肥：立秋后加大肥水供应；5.修剪：需多次摘心以控制株高和花数。",
        "flower_language": "清净、高洁、长寿、真情、隐逸、吉祥。", "plant_type": "草本"
    },
    {
        "name": "水仙花", "family": "石蒜科 水仙属", "color": "白色、淡黄色", "blooming_period": "1月-3月",
        "description": "中国传统名花，有'凌波仙子'的美誉。通常采用水培方式。",
        "care_guide": "1.光照：喜阳光，阳光不足会导致叶片徒长；2.水分：勤换水，保持水质清澈；3.温度：喜凉爽，温度过高开花期会缩短；4.肥料：一般水培无需额外施肥；5.雕刻：可通过雕刻球茎控制生长形态。",
        "flower_language": "多情、想你、纯洁、吉祥、团圆。", "plant_type": "草本"
    },
    {
        "name": "君子兰", "family": "石蒜科 君子兰属", "color": "橙红色、黄色", "blooming_period": "1月-5月",
        "description": "观叶赏花兼具的名贵花卉。叶片肥厚，整齐排列，花朵端庄。",
        "care_guide": "1.光照：喜散射光，忌强光直射叶片；2.水分：肉质根，耐旱怕涝；3.土壤：透气性好的腐叶土；4.施肥：喜肥，尤其需要磷钾肥；5.转向：每周转动盆向180度，防止叶片长歪。",
        "flower_language": "高贵、有君子之风、富贵、长寿、幸福。", "plant_type": "草本"
    },
    {
        "name": "雏菊", "family": "菊科 雏菊属", "color": "白、粉、红", "blooming_period": "3月-6月",
        "description": "多年生草本，常作二年生栽培。植株矮小，花朵玲珑可爱。",
        "care_guide": "1.光照：喜阳光充足，耐半阴；2.水分：保持土壤湿润，不可积水；3.土壤：排水良好的肥沃壤土；4.温度：喜凉爽，忌高温多湿；5.施肥：每半月施一次复合肥。",
        "flower_language": "纯洁、天真、深藏在心底的爱、快乐、希望。", "plant_type": "草本"
    },
    {
        "name": "长寿花", "family": "景天科 伽蓝菜属", "color": "红、橙、黄、粉、紫", "blooming_period": "12月-5月",
        "description": "多肉植物，花朵密集，花期极长。叶片肥厚，四季常青。",
        "care_guide": "1.光照：喜阳光，阳光充足时叶片边缘会泛红；2.水分：耐旱，保持土壤微干；3.土壤：疏松透气的多肉专用土；4.施肥：花期前多施磷钾肥；5.控光：短日照处理可促使提前开花。",
        "flower_language": "大吉大利、长命百岁、福寿安康、坚忍不拔。", "plant_type": "多肉"
    },
    {
        "name": "风信子", "family": "天门冬科 风信子属", "color": "蓝、紫、白、粉、红、黄", "blooming_period": "3月-4月",
        "description": "球根花卉，花序呈圆柱状，花朵密集，香气极浓。",
        "care_guide": "1.光照：喜光，全日照或半日照均可；2.水分：水培需定期换水，土培保持湿润；3.温度：喜凉爽耐寒；4.肥料：花期无需额外肥水；5.防毒：种球表皮有毒，接触后需洗手。",
        "flower_language": "喜悦、竞赛、赌注、游戏、悲哀、忧郁的爱。", "plant_type": "草本"
    },
    {
        "name": "矮牵牛", "family": "茄科 矮牵牛属", "color": "紫、红、白、粉及各种斑纹", "blooming_period": "4月-11月",
        "description": "多年生草本，常作一二年生栽培。花期极长，色彩最丰富的草花之一。",
        "care_guide": "1.光照：极度喜光，光照不足会导致开花减少；2.水分：喜湿润，夏季高温需早晚浇水；3.土壤：排水良好的砂质土；4.修剪：通过掐尖促进分枝，花后修剪促二次开花；5.施肥：薄肥勤施，每周施一次稀薄液肥。",
        "flower_language": "安全感、与你同心、有你我就觉得温馨。", "plant_type": "草本"
    },
    {
        "name": "吊兰", "family": "天门冬科 吊兰属", "color": "白色小花", "blooming_period": "5月-8月",
        "description": "极受欢迎的室内观叶植物。具有强大的空气净化能力，能吸收甲醛。",
        "care_guide": "1.光照：喜半阴，夏季需避开直射光；2.水分：喜湿润，生长期需充足肥水；3.土壤：排水良好的腐殖土；4.修剪：及时剪除枯黄叶片；5.施肥：每月施一次薄氮肥。",
        "flower_language": "无奈而又给人希望、纯洁、朴实。", "plant_type": "草本"
    },
    {
        "name": "红掌", "family": "天南星科 花烛属", "color": "红色、粉色、白色", "blooming_period": "全年",
        "description": "常绿草本，佛焰苞鲜艳夺目，具有腊质感。花期持久。",
        "care_guide": "1.光照：喜散射光，忌强光直射；2.水分：喜湿润环境，保持土壤微湿；3.湿度：喜高湿度，需经常向叶片喷雾；4.土壤：透气透水的泥炭土；5.温度：喜温暖，低于15度生长缓慢。",
        "flower_language": "大展宏图、热情、热血、进取、欣欣向荣。", "plant_type": "草本"
    },
    {
        "name": "仙人掌", "family": "仙人掌科 仙人掌属", "color": "黄、红、橙、紫", "blooming_period": "5月-7月",
        "description": "典型的沙漠植物，茎肉质多浆，叶退化为刺。极其耐旱。",
        "care_guide": "1.光照：极度喜光，尽量多晒太阳；2.水分：极其耐旱，宁干勿湿；3.土壤：排水极佳的砂质土或颗粒土；4.施肥：生长期每月施一次极稀薄的复合肥；5.温度：喜温暖，北方冬季需断水防冻。",
        "flower_language": "坚强、刚毅、外冷内热、温暖的回忆、坚持到底。", "plant_type": "多肉"
    },
    {
        "name": "桂花", "family": "木犀科 木犀属", "color": "金黄、淡黄、橙红、白色", "blooming_period": "9月-10月",
        "description": "中国传统十大名花之一。集绿化、美化、香化于一体的优良园林树种。",
        "care_guide": "1.光照：喜光，每天至少8小时光照；2.水分：耐旱不耐涝，盆土见干见湿；3.土壤：微酸性砂质壤土；4.施肥：喜猪粪等有机肥；5.修剪：每年花后或春季萌芽前适当修剪。",
        "flower_language": "崇高、贞洁、荣誉、友好、吉祥、收获。", "plant_type": "木本"
    },
    {
        "name": "三角梅", "family": "紫茉莉科 叶子花属", "color": "红、紫、粉、橙、白、黄", "blooming_period": "11月-次年6月（南方地区）",
        "description": "木质藤本状灌木。色彩鲜艳的部分实际上是苞片而非花瓣。",
        "care_guide": "1.光照：极度喜光，光照不足会导致落叶不长花；2.水分：耐旱，花期前适当控水可促花；3.土壤：排水良好的砂质土；4.施肥：喜肥，尤其需多施磷钾肥；5.修剪：生长期需重剪以维持株型。",
        "flower_language": "热情、坚韧不拔、顽强奋斗、没有真爱是一种悲伤。", "plant_type": "藤本"
    },
    {
        "name": "一品红", "family": "大戟科 大戟属", "color": "红色、黄色、白色", "blooming_period": "10月-次年4月",
        "description": "灌木植物，顶端苞叶鲜红，常用于圣诞节和春节装饰。",
        "care_guide": "1.光照：喜阳光，短日照植物；2.水分：喜湿润，但忌积水导致烂根；3.土壤：肥沃疏松的砂质壤土；4.温度：喜温暖，不耐寒；5.控色：控制光照时间可使苞叶变色。",
        "flower_language": "我的心正在燃烧、绘出美好的明天、祝福、成功。", "plant_type": "木本"
    },
    {
        "name": "杜鹃花", "family": "杜鹃花科 杜鹃花属", "color": "红、粉、紫、白", "blooming_period": "4月-5月",
        "description": "中国三大名花之一。花冠漏斗状，色彩艳丽，繁花似锦。",
        "care_guide": "1.光照：喜半阴，忌烈日暴晒；2.土壤：必须是肥沃的酸性土壤（腐叶土）；3.水分：喜湿润，保持土壤微湿；4.施肥：施薄肥，切忌浓肥；5.温度：喜凉爽湿润，不耐严寒酷暑。",
        "flower_language": "永远属于你、克制、节制、诚信、思乡、繁荣。", "plant_type": "木本"
    },
    {
        "name": "蝴蝶兰", "family": "兰科 蝴蝶兰属", "color": "紫、红、白、黄、各种斑纹", "blooming_period": "春节前后",
        "description": "有'洋兰王后'之称。花朵形如蝴蝶在飞舞，姿态优美。",
        "care_guide": "1.光照：喜散射光，忌强光；2.水分：喜湿润，但忌基质积水；3.基质：专用的水苔或树皮；4.温度：喜温暖，越冬温度需在15度以上；5.施肥：生长期薄肥勤施。",
        "flower_language": "我爱你、幸福向你飞来、高洁、典雅。", "plant_type": "草本"
    },
    {
        "name": "牵牛花", "family": "旋花科 牵牛属", "color": "蓝、紫、红、白、粉", "blooming_period": "6月-10月",
        "description": "一年生缠绕草本。花冠漏斗状，清晨开放，中午即萎蔫。",
        "care_guide": "1.光照：喜阳光充足，耐半阴；2.水分：喜湿润环境，夏季需多浇水；3.土壤：适应性强，对土壤要求不高；4.支撑：需设立支架供其攀援；5.施肥：生长期每半月施一次复合肥。",
        "flower_language": "名誉、爱情永固、冷静、虚幻、易碎的爱。", "plant_type": "藤本"
    },
    {
        "name": "大丽花", "family": "菊科 大丽花属", "color": "除蓝色外几乎所有颜色", "blooming_period": "6月-12月",
        "description": "多年生草本，具有巨大的块根。花朵硕大，花瓣整齐，品种极其丰富。",
        "care_guide": "1.光照：喜光，但在夏季高温时需适当遮阴；2.水分：喜湿润但忌积水，避免烂根；3.土壤：排水良好的肥沃砂质土；4.施肥：喜肥，生长期需充足氮磷钾；5.修剪：及时抹除腋芽以保证主花硕大。",
        "flower_language": "大吉大利、新颖、感激、背叛、毅力。", "plant_type": "草本"
    },
    {
        "name": "朱顶红", "family": "石蒜科 石蒜属", "color": "红、粉、白、各种条纹", "blooming_period": "春季、初夏",
        "description": "球根花卉，花梗粗壮中空，花朵硕大如喇叭，极其艳丽。",
        "care_guide": "1.光照：喜充足散射光，忌暴晒；2.水分：土培见干见湿，不可积水；3.土壤：疏松、肥沃的腐叶土；4.肥料：花前追施磷钾肥；5.休眠：冬季落叶后进入休眠，需停止浇水。",
        "flower_language": "渴望被爱、追求爱、成双成对、勇敢、追求。", "plant_type": "草本"
    },
    {
        "name": "非洲菊", "family": "菊科 非洲菊属", "color": "红、橙、黄、粉、白", "blooming_period": "11月-次年4月",
        "description": "又名太阳花、扶郎花。花朵大而色彩明快，常作为切花使用。",
        "care_guide": "1.光照：喜光，全日照开花多；2.水分：保持土壤湿润，不可从花心浇水；3.土壤：深厚肥沃的砂质壤土；4.温度：喜温暖，不耐寒；5.施肥：生长期每周施一次复合肥。",
        "flower_language": "互敬互爱、毅力、不怕艰难、永远快乐、欣欣向荣。", "plant_type": "草本"
    },
    {
        "name": "栀子", "family": "茜草科 栀子属", "color": "白色", "blooming_period": "5-7月",
        "description": "常绿灌木，叶色翠绿，花朵芳香四溢，洁白如雪。",
        "care_guide": "1.光照：喜光，但夏季忌烈日；2.土壤：喜酸性土壤；3.浇水：喜湿润，常向叶片喷水；4.施肥：施薄肥，切忌浓肥；5.修剪：花后及时剪除残花。",
        "flower_language": "喜悦、永恒的爱、一生的守候。", "plant_type": "木本"
    },
    {
        "name": "紫罗兰", "family": "十字花科 紫罗兰属", "color": "紫、红、白、蓝", "blooming_period": "4月-5月",
        "description": "多年生草本，常作二年生栽培。花朵繁茂，气味清香。",
        "care_guide": "1.光照：喜冷凉气候，忌燥热，喜充足阳光；2.水分：保持土壤微湿；3.土壤：肥沃疏松的中性或微碱性土；4.施肥：生长期每10天施一次薄肥；5.温度：耐寒性较强。",
        "flower_language": "永恒的美、质朴、美德、清凉、清淡。", "plant_type": "草本"
    },
    {
        "name": "虞美人", "family": "罂粟科 罂粟属", "color": "红、紫、白、粉", "blooming_period": "3月-8月",
        "description": "一年生草本。花瓣极薄，质地如丝，随风摇曳，姿态绰约。",
        "care_guide": "1.光照：喜阳光充足，耐寒；2.水分：忌积水，盆土见干见湿；3.土壤：排水良好的肥沃砂壤土；4.施肥：生长期每20天施肥一次；5.环境：忌高温多湿。",
        "flower_language": "安慰、慰问、生离死别、悲歌、热烈。", "plant_type": "草本"
    },
    {
        "name": "倒挂金钟", "family": "柳叶菜科 倒挂金钟属", "color": "红、紫、粉、白", "blooming_period": "4月-12月",
        "description": "半灌木植物。花朵下垂，形如灯笼或铃铛，极其精美。",
        "care_guide": "1.光照：喜凉爽湿润环境，夏季必须遮阴降温；2.水分：生长期保持湿润，忌积水；3.土壤：肥沃疏松的微酸性土壤；4.施肥：薄肥勤施；5.越夏：极其怕热，需在通风阴凉处。",
        "flower_language": "相信爱情、热烈的心、诚实、感谢。", "plant_type": "木本"
    },
    {
        "name": "瑞香", "family": "瑞香科 瑞香属", "color": "紫红、白色", "blooming_period": "3月-5月",
        "description": "常绿灌木。花朵小而密集，香气浓郁，有'千里香'之称。",
        "care_guide": "1.光照：喜半阴，夏季需遮阴；2.水分：肉质根，怕涝，保持土壤微干；3.土壤：肥沃疏松的微酸性腐叶土；4.施肥：施薄肥，忌生肥浓肥；5.温度：喜温暖凉爽，不耐严寒。",
        "flower_language": "吉祥、荣誉、不朽、高尚。", "plant_type": "木本"
    },
    {
        "name": "满天星", "family": "石竹科 丝石竹属", "color": "白色、粉色", "blooming_period": "5月-8月",
        "description": "多年生草本。花朵极小，如繁星点点，是著名的鲜切花配材。",
        "care_guide": "1.光照：喜阳光，阳光不足会导致株型松散；2.水分：耐旱不耐涝；3.土壤：排水良好的碱性土壤；4.温度：喜冷凉，忌高温；5.施肥：生长期每15天施一次磷钾肥。",
        "flower_language": "清纯、关怀、恋爱、配角、真爱、纯洁的心灵。", "plant_type": "草本"
    },
    {
        "name": "石斛兰", "family": "兰科 石斛属", "color": "白、黄、紫、粉", "blooming_period": "1月-6月",
        "description": "附生草本植物。花姿优美，具有极高的观赏价值和药用价值。",
        "care_guide": "1.光照：喜半阴，忌烈日暴晒；2.水分：喜湿润，每天喷雾增加湿度；3.基质：树皮、碎石、水苔等透气基质；4.温度：喜温暖，不耐寒；5.施肥：施专用兰肥，少量多次。",
        "flower_language": "坚毅、勇敢、欢迎、慈爱、祝福。", "plant_type": "草本"
    },
    {
        "name": "荷花", "family": "莲科 莲属", "color": "红、粉、白、黄", "blooming_period": "6月-9月",
        "description": "水生植物，有'出淤泥而不染'的高洁品质。叶片圆大，花朵清丽。",
        "care_guide": "1.光照：全日照，光照不足会导致不开花；2.水分：不可缺水，水位根据植株大小调整；3.土壤：肥沃的河泥或塘泥；4.施肥：施足底肥，生长期施磷钾肥；5.温度：喜温暖，夏季生长旺盛。",
        "flower_language": "清白、高尚、纯洁、坚贞、忠贞、信仰。", "plant_type": "草本"
    },
    {
        "name": "睡莲", "family": "睡莲科 睡莲属", "color": "白、蓝、红、黄、粉", "blooming_period": "6月-8月",
        "description": "水生花卉，浮水植物。花朵白天开放，夜晚闭合，如'睡美人'。",
        "care_guide": "1.光照：喜阳光，每天需6小时以上直射光；2.水深：根据品种不同要求水深在20-100厘米；3.土壤：肥沃的粘性土壤；4.温度：喜温暖，不耐寒；5.越冬：冬季需保持泥土不结冰。",
        "flower_language": "洁净、纯真、妖艳、清纯、纯洁。", "plant_type": "草本"
    },
    {
        "name": "非洲紫罗兰", "family": "苦苣苔科 非洲堇属", "color": "蓝、紫、粉、白", "blooming_period": "全年",
        "description": "又名非洲堇。植株小巧，花色丰富，极适合室内盆栽。",
        "care_guide": "1.光照：喜半阴，忌强光直射；2.水分：保持土壤微湿，切忌将水洒在叶片上（会导致烂斑）；3.土壤：疏松透气的泥炭土；4.施肥：每月施一次极稀薄液肥；5.温度：喜温暖，越冬不低于10度。",
        "flower_language": "永恒的爱、亲切、微笑、小小幸福。", "plant_type": "草本"
    },
    {
        "name": "旱金莲", "family": "旱金莲科 旱金莲属", "color": "红、橙、黄", "blooming_period": "6月-10月",
        "description": "半蔓生植物。叶片形如荷叶，花朵色泽艳丽，全株可食。",
        "care_guide": "1.光照：喜充足阳光，耐半阴；2.水分：喜湿润但忌积水；3.土壤：疏松肥沃的排水良好的土壤；4.施肥：忌施浓肥，氮肥过多会光长叶不开花；5.支撑：需设立支架供攀爬。",
        "flower_language": "爱国、不屈不挠、顺其自然、开心。", "plant_type": "藤本"
    },
    {
        "name": "大岩桐", "family": "苦苣苔科 大岩桐属", "color": "红、紫、白、蓝、粉", "blooming_period": "3月-8月",
        "description": "多年生草本。花冠大而钟状，质感如天鹅绒，极其艳丽。",
        "care_guide": "1.光照：喜散射光，忌强光直射；2.水分：保持盆土湿润，忌叶面喷水（易烂叶）；3.土壤：疏松肥沃的腐叶土；4.施肥：生长期每半月施一次复合肥；5.休眠：花后进入半休眠期，需控水。",
        "flower_language": "华丽、欲望、欲望与追求。", "plant_type": "草本"
    },
    {
        "name": "口红吊兰", "family": "苦苣苔科 芒毛苣苔属", "color": "红色", "blooming_period": "11月-次年6月",
        "description": "常绿蔓生植物。花萼筒状，花冠伸出如口红，极其奇特。",
        "care_guide": "1.光照：喜半阴，忌强光暴晒；2.水分：喜湿润，经常喷雾；3.土壤：排水良好的泥炭土或椰砖；4.施肥：生长期每月施一次磷钾肥；5.温度：喜温暖，越冬需15度以上。",
        "flower_language": "美丽、绚烂、美艳、热情、执着。", "plant_type": "藤本"
    },
    {
        "name": "蟹爪兰", "family": "仙人掌科 蟹爪兰属", "color": "红、粉、紫、白、黄", "blooming_period": "10月-次年2月",
        "description": "附生肉质植物。节径如蟹爪，花朵垂挂于顶端，色彩艳丽。",
        "care_guide": "1.光照：喜半阴，短日照植物可促花；2.水分：耐旱怕涝，保持盆土见干见湿；3.土壤：疏松透气的颗粒土；4.施肥：花芽分化期多施磷钾肥；5.温度：喜凉爽，不耐高温。",
        "flower_language": "鸿运当头、锦上添花、热情、坚韧。", "plant_type": "多肉"
    },
    {
        "name": "一叶兰", "family": "天门冬科 蜘蛛抱蛋属", "color": "紫色（花极罕见）", "blooming_period": "春季",
        "description": "极具生命力的室内观叶植物。叶片挺拔，四季常青，极其耐阴。",
        "care_guide": "1.光照：极其耐阴，光照过强会导致叶片变黄；2.水分：耐旱，保持盆土微润即可；3.土壤：适应性极强，排水良好即可；4.施肥：生长期施稀薄氮肥；5.清洁：定期擦拭叶片灰尘。",
        "flower_language": "坚韧、长寿、不屈不挠、吉祥。", "plant_type": "草本"
    },
    {
        "name": "金边瑞香", "family": "瑞香科 瑞香属", "color": "紫红、白色", "blooming_period": "2月-5月",
        "description": "瑞香的变种。叶缘金黄色，花香极其浓郁，有'活的香水'之称。",
        "care_guide": "1.光照：喜半阴，夏季需遮阴；2.水分：肉质根，怕水涝，保持微干；3.土壤：肥沃疏松的微酸性土；4.施肥：施薄肥，忌生肥浓肥；5.环境：喜通风，忌闷热。",
        "flower_language": "吉祥、荣誉、不朽、高尚、出类拔萃。", "plant_type": "木本"
    },
    {
        "name": "文竹", "family": "天门冬科 天门冬属", "color": "白色小花", "blooming_period": "9月-10月",
        "description": "常绿藤本状草本。叶片轻盈如羽毛，姿态幽雅，常用于盆景。",
        "care_guide": "1.光照：喜半阴，忌强光直射；2.水分：喜湿润但忌积水，盆土见干见湿；3.湿度：喜高湿度，经常喷雾；4.施肥：施薄肥，忌浓肥；5.修剪：及时剪除黄叶，通过修剪控制造型。",
        "flower_language": "永恒、友谊长存、纯洁的心、博爱。", "plant_type": "草本"
    },
    {
        "name": "发财树", "family": "锦葵科 瓜栗属", "color": "淡黄色花", "blooming_period": "5月-11月",
        "description": "常绿乔木。掌状复叶，寓意财源滚滚，是极其普遍的室内绿植。",
        "care_guide": "1.光照：喜阳光也耐半阴；2.水分：极度怕积水，必须保持盆土微干；3.土壤：排水良好的砂质土；4.温度：喜温暖，不耐寒，低于10度易受冻；5.施肥：生长期每月施一次复合肥。",
        "flower_language": "招财进宝、兴旺发达、事业有成。", "plant_type": "木本"
    },
    {
        "name": "平安树", "family": "樟科 肉桂属", "color": "白色小花", "blooming_period": "6月-8月",
        "description": "常绿乔木。叶片翠绿挺拔，寓意家人平安，具有净化空气的作用。",
        "care_guide": "1.光照：喜光也耐半阴，夏季遮阴；2.水分：喜湿润，保持土壤湿润不积水；3.土壤：肥沃疏松的微酸性土；4.施肥：生长期每月施一次氮肥；5.温度：喜温暖，不耐严寒。",
        "flower_language": "祈求平安、阖家幸福、万事如意。", "plant_type": "木本"
    }
]

async def migrate():
    # 自动执行 DDL 变更：添加 plant_type 字段（如果不存在）
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE flowers ADD COLUMN plant_type VARCHAR(64)"))
            print("Successfully added plant_type column to flowers table.")
        except Exception as e:
            if "Duplicate column name" in str(e) or "1060" in str(e):
                print("Column plant_type already exists.")
            else:
                print(f"Error adding column: {e}")

    async with AsyncSessionFactory() as db:
        for data in flowers_data:
            # 检查是否已存在
            stmt = select(Flower).filter(Flower.name == data["name"])
            res = await db.execute(stmt)
            existing = res.scalars().first()
            
            if not existing:
                flower = Flower(**data)
                db.add(flower)
                print(f"Added: {data['name']}")
            else:
                # 更新现有数据
                existing.family = data["family"]
                existing.color = data["color"]
                existing.blooming_period = data["blooming_period"]
                existing.description = data["description"]
                existing.care_guide = data["care_guide"]
                existing.flower_language = data["flower_language"]
                existing.plant_type = data["plant_type"]
                print(f"Updated: {data['name']}")
        
        await db.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(migrate())
