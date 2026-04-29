from typing import Any
import asyncio
from sqlalchemy import inspect, select
from app.services.db import AsyncSessionFactory
from app.models.tables import Comment, CommentReply, Favorite, Feedback, Flower, User, UserProfile
from app.core.security import get_password_hash

SEED_USERS: list[dict[str, str]] = [
    {"username": "花世界管理员", "email": "admin@huashijie.com", "password": "Admin@2026", "role": "admin", "nickname": "花世界管理员", "bio": "负责后台内容审核、知识库维护和社区秩序管理。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=admin-cn"},
    {"username": "内容审核员小顾", "email": "content.gu@huashijie.com", "password": "Content@2026", "role": "admin", "nickname": "小顾", "bio": "日常负责花卉资料校对、评论审核和专题内容编排。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=gu-cn"},
    {"username": "运营小何", "email": "ops.he@huashijie.com", "password": "Ops@2026", "role": "admin", "nickname": "运营小何", "bio": "关注用户反馈和活动运营，希望把社区氛围做得更真实。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=he-cn"},
    {"username": "林小雨", "email": "lin.xiaoyu@example.com", "password": "Xiaoyu@2026", "role": "user", "nickname": "小雨同学", "bio": "阳台园艺爱好者，常记录月季和绣球的花期变化。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=lin-cn"},
    {"username": "陈一帆", "email": "chen.yifan@example.com", "password": "Yifan@2026", "role": "user", "nickname": "一帆Plant", "bio": "摄影社成员，喜欢在校园和植物园拍花。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=chen-cn"},
    {"username": "周梦洁", "email": "zhou.mengjie@example.com", "password": "Mengjie@2026", "role": "user", "nickname": "梦洁", "bio": "偏爱香味花卉，尤其喜欢兰花和栀子。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=zhou-cn"},
    {"username": "吴皓然", "email": "wu.haoran@example.com", "password": "Haoran@2026", "role": "user", "nickname": "皓然", "bio": "新手植物玩家，靠知识库认识常见花。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=wu-cn"},
    {"username": "唐诗雨", "email": "tang.shiyu@example.com", "password": "Shiyu@2026", "role": "user", "nickname": "诗雨", "bio": "花店兼职店员，关注花语和节日搭配。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=tang-cn"},
    {"username": "苏清禾", "email": "su.qinghe@example.com", "password": "Qinghe@2026", "role": "user", "nickname": "清禾", "bio": "喜欢木本花卉和庭院植物。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=su-cn"},
    {"username": "许南栀", "email": "xu.nanzhi@example.com", "password": "Nanzhi@2026", "role": "user", "nickname": "南栀", "bio": "对香花植物和观花藤本特别感兴趣。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=xu-cn"},
    {"username": "顾景澄", "email": "gu.jingcheng@example.com", "password": "Jingcheng@2026", "role": "user", "nickname": "景澄", "bio": "比较喜欢仙人掌和多肉植物。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=jingcheng-cn"},
    {"username": "赵知夏", "email": "zhao.zhixia@example.com", "password": "Zhixia@2026", "role": "user", "nickname": "知夏", "bio": "喜欢记录四季花讯。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=zhixia-cn"},
    {"username": "沈月白", "email": "shen.yuebai@example.com", "password": "Yuebai@2026", "role": "user", "nickname": "月白", "bio": "偏爱白色系花卉和夜香植物。", "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=yuebai-cn"},
]

SEED_COMMENTS = [
    {"username": "林小雨", "flower_name": "月季", "content": "我家阳台的月季按这里的建议修剪后，花量明显稳定了。", "status": "approved"},
    {"username": "陈一帆", "flower_name": "向日葵", "content": "向日葵真的很适合夏天拍照，逆光尤其好看。", "status": "approved"},
    {"username": "周梦洁", "flower_name": "兰花", "content": "兰花湿度控制特别关键，这条说明对新手很友好。", "status": "approved"},
    {"username": "吴皓然", "flower_name": "百合", "content": "第一次知道百合怕闷热，之前一直养不好总算找到原因。", "status": "approved"},
    {"username": "唐诗雨", "flower_name": "玫瑰", "content": "玫瑰花语这块整理得很完整，做节日选花参考很方便。", "status": "approved"},
    {"username": "苏清禾", "flower_name": "茶花", "content": "茶花在南方冬春季特别有观赏性，偏酸性土这一点很重要。", "status": "approved"},
    {"username": "许南栀", "flower_name": "风车茉莉", "content": "风车茉莉做阳台围栏植物真的很好看，香味也温柔。", "status": "approved"},
    {"username": "顾景澄", "flower_name": "蟹爪兰", "content": "蟹爪兰冬天开花的时候特别喜庆，控水真的有用。", "status": "approved"},
    {"username": "赵知夏", "flower_name": "菊花", "content": "秋季筛选里菊花一定要有，文化感和季节感都很强。", "status": "approved"},
    {"username": "沈月白", "flower_name": "栀子花", "content": "栀子花开的时候很香，希望后面能加黄叶专题。", "status": "approved"},
    {"username": "内容审核员小顾", "flower_name": "郁金香", "content": "这条百科内容已经过复核，后续会继续补充园艺品种说明。", "status": "approved"},
    {"username": "运营小何", "flower_name": "绣球", "content": "绣球一直是热门花卉，用户讨论和收藏量都很高。", "status": "approved"},
]

SEED_REPLIES = [
    {"comment_user": "林小雨", "flower_name": "月季", "comment_content": "我家阳台的月季按这里的建议修剪后，花量明显稳定了。", "username": "内容审核员小顾", "content": "后面我们会继续补月季病虫害和不同品种的专题内容。"},
    {"comment_user": "陈一帆", "flower_name": "向日葵", "comment_content": "向日葵真的很适合夏天拍照，逆光尤其好看。", "username": "赵知夏", "content": "和荷花一起做夏季专题的话，画面感会特别强。"},
    {"comment_user": "周梦洁", "flower_name": "兰花", "comment_content": "兰花湿度控制特别关键，这条说明对新手很友好。", "username": "沈月白", "content": "我后来加了加湿托盘，花苞状态确实稳定很多。"},
    {"comment_user": "吴皓然", "flower_name": "百合", "comment_content": "第一次知道百合怕闷热，之前一直养不好总算找到原因。", "username": "林小雨", "content": "球根类花卉排水真的很关键，尤其夏天。"},
    {"comment_user": "唐诗雨", "flower_name": "玫瑰", "comment_content": "玫瑰花语这块整理得很完整，做节日选花参考很方便。", "username": "运营小何", "content": "后面我们会考虑再做一个节日送花专题。"},
    {"comment_user": "苏清禾", "flower_name": "茶花", "comment_content": "茶花在南方冬春季特别有观赏性，偏酸性土这一点很重要。", "username": "周梦洁", "content": "对，和杜鹃一样，配土不对的话状态就会差很多。"},
]

SEED_FAVORITES: list[dict[str, Any]] = [
    {"username": "林小雨", "flower_names": ["月季", "绣球", "百合", "郁金香", "茶花"]},
    {"username": "陈一帆", "flower_names": ["向日葵", "樱花", "玫瑰", "薰衣草"]},
    {"username": "周梦洁", "flower_names": ["兰花", "茉莉花", "栀子花", "白兰花"]},
    {"username": "吴皓然", "flower_names": ["向日葵", "月季", "菊花", "金盏花"]},
    {"username": "唐诗雨", "flower_names": ["玫瑰", "郁金香", "风信子", "洋桔梗", "满天星"]},
    {"username": "苏清禾", "flower_names": ["茶花", "杜鹃", "紫薇", "木槿", "桂花"]},
    {"username": "许南栀", "flower_names": ["风车茉莉", "牵牛花", "凌霄花", "铁线莲"]},
    {"username": "顾景澄", "flower_names": ["蟹爪兰", "仙人球", "令箭荷花", "昙花"]},
]

SEED_FEEDBACKS: list[dict[str, Any]] = [
    {"username": "林小雨", "flower_name": "月季", "content": "希望月季页面能增加常见病虫害图文示例。", "status": "processing", "reply_content": "已记录到内容增强需求中。"},
    {"username": "陈一帆", "flower_name": "向日葵", "content": "建议识花结果页支持一键复制植物名称。", "status": "resolved", "reply_content": "该需求已纳入下个版本。"},
    {"username": "周梦洁", "flower_name": "兰花", "content": "后面如果能细分春兰、蕙兰和蝴蝶兰会更专业。", "status": "pending", "reply_content": None},
    {"username": "吴皓然", "flower_name": None, "content": "建议首页再增加一个适合入门花卉的专题入口。", "status": "closed", "reply_content": "感谢建议，后续会统一规划。"},
]

FLOWER_DATA: list[dict[str, str | None]] = []

FLOWER_SERIES: list[dict[str, Any]] = [
    {"family": "蔷薇科", "plant_type": "木本", "status": "published", "season": "春季", "suffix": "花", "names": ["月季", "玫瑰", "蔷薇", "樱花", "海棠", "桃花", "杏花", "李花", "梨花", "梅花", "木香花", "贴梗海棠", "草莓花", "珍珠梅", "绣线菊"]},
    {"family": "菊科", "plant_type": "草本", "status": "published", "season": "夏季", "suffix": "花", "names": ["向日葵", "菊花", "雏菊", "金盏花", "波斯菊", "大丽花", "翠菊", "勋章菊", "玛格丽特", "万寿菊", "非洲菊", "瓜叶菊", "蓝目菊", "天人菊", "姬小菊"]},
    {"family": "兰科", "plant_type": "草本", "status": "published", "season": "全年", "suffix": "兰", "names": ["兰花", "蝴蝶兰", "春兰", "蕙兰", "建兰", "石斛兰", "卡特兰", "文心兰", "兜兰", "万代兰", "寒兰", "墨兰", "大花蕙兰", "白及", "虾脊兰"]},
    {"family": "百合科", "plant_type": "草本", "status": "published", "season": "春季", "suffix": "花", "names": ["百合", "郁金香", "风信子", "铃兰", "玉簪", "萱草", "贝母花", "朱顶红", "葱兰", "韭兰", "天堂鸟", "火焰百合", "水仙", "晚香玉", "六出花"]},
    {"family": "豆科", "plant_type": "木本", "status": "published", "season": "春季", "suffix": "花", "names": ["紫藤", "紫荆", "合欢花", "凤凰木", "含羞草", "决明花", "鸡冠刺桐", "槐花", "红花羊蹄甲", "黄槐决明", "金雀花", "紫云英", "羽扇豆", "金链花", "相思树花"]},
    {"family": "仙人掌科", "plant_type": "多肉", "status": "published", "season": "夏季", "suffix": "花", "names": ["昙花", "蟹爪兰", "令箭荷花", "仙人球", "绯花玉", "玉翁", "鼠尾掌", "量天尺花", "毛花柱", "白檀", "金琥花", "仙人指", "火龙果花", "金手指", "龙骨花"]},
    {"family": "山茶科", "plant_type": "木本", "status": "published", "season": "冬季", "suffix": "花", "names": ["茶花", "山茶", "耐冬", "金花茶", "杜鹃红山茶"]},
    {"family": "杜鹃花科", "plant_type": "木本", "status": "published", "season": "春季", "suffix": "花", "names": ["杜鹃", "映山红", "比利时杜鹃", "夏鹃", "高山杜鹃"]},
    {"family": "木兰科", "plant_type": "木本", "status": "published", "season": "春季", "suffix": "花", "names": ["白兰花", "玉兰", "广玉兰", "含笑花", "深山含笑"]},
    {"family": "唇形科", "plant_type": "草本", "status": "published", "season": "夏季", "suffix": "花", "names": ["薰衣草", "鼠尾草", "迷迭香花", "百里香花", "猫薄荷花"]},
    {"family": "锦葵科", "plant_type": "木本", "status": "published", "season": "夏季", "suffix": "花", "names": ["木槿", "扶桑", "蜀葵", "木芙蓉", "秋葵花"]},
    {"family": "夹竹桃科", "plant_type": "木本", "status": "published", "season": "全年", "suffix": "花", "names": ["风车茉莉", "长春花", "鸡蛋花", "夹竹桃", "黄蝉"]},
    {"family": "石竹科", "plant_type": "草本", "status": "published", "season": "春季", "suffix": "花", "names": ["石竹", "康乃馨", "满天星", "美女樱", "福禄考"]},
]

SEASON_PERIODS = {
    "春季": "3月-5月（春季）",
    "夏季": "6月-8月（夏季）",
    "秋季": "9月-11月（秋季）",
    "冬季": "12月-2月（冬季）",
    "全年": "全年（不同地区略有差异）",
}

SEASON_COLORS = {
    "春季": "粉色、白色、紫色",
    "夏季": "红色、黄色、橙色",
    "秋季": "黄色、红色、紫红色",
    "冬季": "白色、红色、粉色",
    "全年": "红色、粉色、白色、紫色",
}

SEASON_TAGS = {
    "春季": "春季,观花,花境",
    "夏季": "夏季,观花,园艺",
    "秋季": "秋季,观花,季节专题",
    "冬季": "冬季,观花,节庆",
    "全年": "全年,观花,常见花卉",
}


def build_flower(name: str, family: str, season: str, plant_type: str, status: str, extra_tags: str = "") -> dict[str, str | None]:
    tags = SEASON_TAGS[season] if not extra_tags else f"{SEASON_TAGS[season]},{extra_tags}"
    return {
        "name": name,
        "family": family,
        "color": SEASON_COLORS[season],
        "blooming_period": SEASON_PERIODS[season],
        "description": f"{name}是知识库中较常见的{family}观赏花卉，花期稳定，适合用于中文花卉识别、知识检索和筛选展示。",
        "care_guide": f"{name}适合放在通风良好、光照合适的位置养护，按照{season}花卉的常规节奏控制水肥，并注意避免长期积水。",
        "flower_language": f"{name}常被视作象征美好、季节感和生活仪式感的花卉。",
        "plant_type": plant_type,
        "status": status,
        "tags": tags,
    }


for series in FLOWER_SERIES:
    for item_name in series["names"]:
        season = str(series["season"])
        if item_name in {"菊花", "桂花", "彼岸花"}:
            season = "秋季"
        elif item_name in {"梅花", "茶花", "水仙", "蝴蝶兰", "蟹爪兰"}:
            season = "冬季"
        elif item_name in {"兰花", "万代兰", "三角梅", "扶桑", "非洲菊"}:
            season = "全年"
        FLOWER_DATA.append(
            build_flower(
                name=str(item_name),
                family=str(series["family"]),
                season=season,
                plant_type=str(series["plant_type"]),
                status=str(series["status"]),
            )
        )

FLOWER_DATA.extend([
    build_flower("桂花", "木犀科", "秋季", "木本", "published", "香花,庭院"),
    build_flower("荷花", "莲科", "夏季", "草本", "published", "水生,传统名花"),
    build_flower("睡莲", "睡莲科", "夏季", "草本", "published", "水生,庭院水景"),
    build_flower("牵牛花", "旋花科", "夏季", "藤本", "published", "藤本,花墙"),
    build_flower("凌霄花", "紫葳科", "夏季", "藤本", "published", "立体绿化,热烈"),
    build_flower("铁线莲", "毛茛科", "春季", "藤本", "published", "花园,品种多"),
    build_flower("牡丹", "芍药科", "春季", "木本", "published", "传统名花,富贵"),
    build_flower("芍药", "芍药科", "春季", "草本", "published", "大花,切花"),
    build_flower("茉莉花", "木犀科", "夏季", "木本", "published", "香花,阳台"),
    build_flower("栀子花", "茜草科", "夏季", "木本", "published", "香花,白花"),
    build_flower("紫薇", "千屈菜科", "夏季", "木本", "published", "花期长,绿化"),
    build_flower("三角梅", "紫茉莉科", "全年", "藤本", "published", "耐热,南方"),
    build_flower("洋桔梗", "龙胆科", "夏季", "草本", "published", "切花,婚礼"),
    build_flower("鸢尾", "鸢尾科", "春季", "草本", "published", "蓝紫,花境"),
    build_flower("美人蕉", "美人蕉科", "夏季", "草本", "published", "热带感,大型"),
    build_flower("金鱼草", "车前科", "春季", "草本", "published", "花坛,切花"),
    build_flower("天竺葵", "牻牛儿苗科", "夏季", "草本", "published", "阳台,盆栽"),
    build_flower("矮牵牛", "茄科", "夏季", "草本", "published", "吊盆,高花量"),
    build_flower("彼岸花", "石蒜科", "秋季", "草本", "published", "秋季,球根"),
    build_flower("绣球", "虎耳草科", "夏季", "木本", "published", "庭院,半阴"),
])


async def seed_flowers():
    async with AsyncSessionFactory() as session:
        created_count = 0
        for flower_data in FLOWER_DATA:
            result = await session.execute(select(Flower).filter(Flower.name == flower_data["name"]))
            exists = result.scalars().first()
            if exists:
                exists.family = str(flower_data["family"])
                exists.color = str(flower_data["color"])
                exists.blooming_period = str(flower_data["blooming_period"])
                exists.description = str(flower_data["description"])
                exists.care_guide = str(flower_data["care_guide"])
                exists.flower_language = str(flower_data["flower_language"])
                exists.plant_type = flower_data["plant_type"]
                exists.status = str(flower_data["status"])
                exists.tags = flower_data["tags"]
                continue

            session.add(
                Flower(
                    name=str(flower_data["name"]),
                    family=str(flower_data["family"]),
                    color=str(flower_data["color"]),
                    blooming_period=str(flower_data["blooming_period"]),
                    description=str(flower_data["description"]),
                    care_guide=str(flower_data["care_guide"]),
                    flower_language=str(flower_data["flower_language"]),
                    plant_type=flower_data["plant_type"],
                    status=str(flower_data["status"]),
                    tags=flower_data["tags"],
                )
            )
            created_count += 1

        await session.commit()
        total_count = len((await session.execute(select(Flower))).scalars().all())
        print(f"Seeded {created_count} flowers. Total flowers in database: {total_count}")


async def seed_users():
    async with AsyncSessionFactory() as session:
        created_count = 0
        updated_profiles = 0
        for user_data in SEED_USERS:
            result = await session.execute(
                select(User).filter(
                    (User.username == user_data["username"]) | (User.email == user_data["email"])
                )
            )
            user = result.scalars().first()
            if not user:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                )
                session.add(user)
                await session.flush()
                created_count += 1

            profile_result = await session.execute(select(UserProfile).filter(UserProfile.user_id == user.id))
            profile = profile_result.scalars().first()
            if not profile:
                session.add(
                    UserProfile(
                        user_id=user.id,
                        nickname=user_data["nickname"],
                        bio=user_data["bio"],
                        avatar_url=user_data["avatar_url"],
                    )
                )
            else:
                profile.nickname = user_data["nickname"]
                profile.bio = user_data["bio"]
                profile.avatar_url = user_data["avatar_url"]
            updated_profiles += 1

        await session.commit()
        print(f"Seeded {created_count} user accounts and synced {updated_profiles} profiles.")


async def seed_comments_favorites_feedbacks():
    async with AsyncSessionFactory() as session:
        users = {user.username: user for user in (await session.execute(select(User))).scalars().all()}
        flowers = {flower.name: flower for flower in (await session.execute(select(Flower))).scalars().all()}
        feedback_columns = {
            column["name"]
            for column in await session.run_sync(
                lambda sync_session: inspect(sync_session.bind).get_columns("feedbacks")
            )
        }

        comment_count = 0
        comment_map: dict[tuple[str, str, str], Comment] = {}
        for item in SEED_COMMENTS:
            user = users.get(item["username"])
            flower = flowers.get(item["flower_name"])
            if not user or not flower:
                continue
            exists = (
                await session.execute(
                    select(Comment).filter(
                        Comment.user_id == user.id,
                        Comment.flower_id == flower.id,
                        Comment.content == item["content"],
                    )
                )
            ).scalars().first()
            if not exists:
                exists = Comment(user_id=user.id, flower_id=flower.id, content=item["content"], status=item["status"])
                session.add(exists)
                await session.flush()
                comment_count += 1
            comment_map[(item["username"], item["flower_name"], item["content"])] = exists

        reply_count = 0
        for item in SEED_REPLIES:
            user = users.get(item["username"])
            comment = comment_map.get((item["comment_user"], item["flower_name"], item["comment_content"]))
            if not comment:
                comment_user = users.get(item["comment_user"])
                flower = flowers.get(item["flower_name"])
                if comment_user and flower:
                    comment = (
                        await session.execute(
                            select(Comment).filter(
                                Comment.user_id == comment_user.id,
                                Comment.flower_id == flower.id,
                                Comment.content == item["comment_content"],
                            )
                        )
                    ).scalars().first()
            if not user or not comment:
                continue
            exists = (
                await session.execute(
                    select(CommentReply).filter(
                        CommentReply.comment_id == comment.id,
                        CommentReply.user_id == user.id,
                        CommentReply.content == item["content"],
                    )
                )
            ).scalars().first()
            if exists:
                continue
            session.add(CommentReply(comment_id=comment.id, user_id=user.id, content=item["content"]))
            reply_count += 1

        favorite_count = 0
        for item in SEED_FAVORITES:
            user = users.get(item["username"])
            if not user:
                continue
            for flower_name in item["flower_names"]:
                flower = flowers.get(flower_name)
                if not flower:
                    continue
                exists = (
                    await session.execute(
                        select(Favorite).filter(Favorite.user_id == user.id, Favorite.flower_id == flower.id)
                    )
                ).scalars().first()
                if exists:
                    continue
                session.add(Favorite(user_id=user.id, flower_id=flower.id))
                favorite_count += 1

        feedback_count = 0
        for item in SEED_FEEDBACKS:
            user = users.get(item["username"])
            flower = flowers.get(item["flower_name"]) if item["flower_name"] else None
            if not user:
                continue
            exists = (
                await session.execute(
                    select(Feedback).filter(Feedback.user_id == user.id, Feedback.content == item["content"])
                )
            ).scalars().first()
            if exists:
                continue
            feedback_data = {"user_id": user.id, "content": item["content"], "status": item["status"]}
            if "flower_id" in feedback_columns:
                feedback_data["flower_id"] = flower.id if flower else None
            if "reply_content" in feedback_columns:
                feedback_data["reply_content"] = item["reply_content"]
            session.add(Feedback(**feedback_data))
            feedback_count += 1

        await session.commit()
        print(f"Seeded {comment_count} comments, {reply_count} replies, {favorite_count} favorites, and {feedback_count} feedback entries.")


async def main():
    await seed_flowers()
    await seed_users()
    await seed_comments_favorites_feedbacks()


if __name__ == "__main__":
    asyncio.run(main())
