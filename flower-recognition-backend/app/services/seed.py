from typing import Any
import asyncio
from sqlalchemy import inspect, select
from app.services.db import AsyncSessionFactory
from app.models.tables import Comment, Favorite, Feedback, Flower, User, UserProfile
from app.core.security import get_password_hash

SEED_USERS: list[dict[str, str]] = [
    {
        "username": "superadmin",
        "email": "superadmin@huashijie.com",
        "password": "Admin@2026",
        "role": "admin",
        "nickname": "系统超管",
        "bio": "负责系统配置、账号管理与演示环境维护。",
        "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=SuperAdmin",
    },
    {
        "username": "content_admin",
        "email": "content.admin@huashijie.com",
        "password": "Content@2026",
        "role": "admin",
        "nickname": "内容管理员",
        "bio": "主要负责花卉百科内容审核、资料修订与评论管理。",
        "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=ContentAdmin",
    },
    {
        "username": "ops_admin",
        "email": "ops.admin@huashijie.com",
        "password": "Ops@2026",
        "role": "admin",
        "nickname": "运营管理员",
        "bio": "负责用户反馈处理、活动运营与日常后台巡检。",
        "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=OpsAdmin",
    },
    {
        "username": "lin_xiaoyu",
        "email": "lin.xiaoyu@example.com",
        "password": "Xiaoyu@2026",
        "role": "user",
        "nickname": "小雨同学",
        "bio": "阳台园艺爱好者，最近在尝试把月季和百合养得更稳定。",
        "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=LinXiaoyu",
    },
    {
        "username": "chen_yifan",
        "email": "chen.yifan@example.com",
        "password": "Yifan@2026",
        "role": "user",
        "nickname": "一帆Plant",
        "bio": "摄影社成员，喜欢记录校园里四季开花植物的变化。",
        "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=ChenYifan",
    },
    {
        "username": "zhou_mengjie",
        "email": "zhou.mengjie@example.com",
        "password": "Mengjie@2026",
        "role": "user",
        "nickname": "梦洁",
        "bio": "偏爱香花植物，尤其喜欢兰花和栀子，常在家里做养护记录。",
        "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=ZhouMengjie",
    },
    {
        "username": "wu_haoran",
        "email": "wu.haoran@example.com",
        "password": "Haoran@2026",
        "role": "user",
        "nickname": "皓然",
        "bio": "新手植物玩家，主要靠识花系统认识小区和公园里的花。",
        "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=WuHaoran",
    },
    {
        "username": "tang_shiyu",
        "email": "tang.shiyu@example.com",
        "password": "Shiyu@2026",
        "role": "user",
        "nickname": "诗雨",
        "bio": "花店兼职店员，日常关注花语、搭配和不同花材的观赏期。",
        "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=TangShiyu",
    },
]

SEED_COMMENTS: list[dict[str, str]] = [
    {"username": "lin_xiaoyu", "flower_name": "月季", "content": "我家阳台的月季今年开得特别勤，按照这里的浇水建议调整后状态稳定很多。", "status": "approved"},
    {"username": "chen_yifan", "flower_name": "向日葵", "content": "学校花坛这批向日葵长势很整齐，拍照时在逆光下特别出片。", "status": "approved"},
    {"username": "zhou_mengjie", "flower_name": "兰花", "content": "兰花的湿度控制确实很关键，空气干燥时花苞容易发黄。", "status": "approved"},
    {"username": "wu_haoran", "flower_name": "百合", "content": "第一次知道百合怕闷热，这条养护信息对我这种新手特别友好。", "status": "approved"},
    {"username": "tang_shiyu", "flower_name": "玫瑰", "content": "玫瑰的花语整理得很完整，适合做节日选花参考。", "status": "approved"},
    {"username": "content_admin", "flower_name": "郁金香", "content": "这条百科内容已经过后台复核，后续会继续补充更多品种说明。", "status": "approved"},
]

SEED_FAVORITES: list[dict[str, Any]] = [
    {"username": "lin_xiaoyu", "flower_names": ["月季", "百合", "郁金香"]},
    {"username": "chen_yifan", "flower_names": ["向日葵", "玫瑰"]},
    {"username": "zhou_mengjie", "flower_names": ["兰花", "百合"]},
    {"username": "wu_haoran", "flower_names": ["向日葵", "月季"]},
    {"username": "tang_shiyu", "flower_names": ["玫瑰", "郁金香", "兰花"]},
]

SEED_FEEDBACKS: list[dict[str, Any]] = [
    {"username": "lin_xiaoyu", "flower_name": "月季", "content": "希望在月季页面增加常见病虫害识别示例，方便阳台种植用户快速排查。", "status": "processing", "reply_content": "已记录到内容增强需求中，后续会补充病虫害图文说明。"},
    {"username": "chen_yifan", "flower_name": "向日葵", "content": "建议识花结果页支持一键复制植物名称，做拍摄整理时会更方便。", "status": "resolved", "reply_content": "该需求已纳入下个前端迭代版本。"},
    {"username": "zhou_mengjie", "flower_name": "兰花", "content": "兰花分类很多，后面如果能细分春兰、蕙兰会更专业。", "status": "pending", "reply_content": None},
    {"username": "wu_haoran", "flower_name": None, "content": "新手引导很有帮助，建议首页再增加一个\"适合入门的花\"专题入口。", "status": "closed", "reply_content": "感谢建议，运营侧会结合专题活动统一规划。"},
    {"username": "tang_shiyu", "flower_name": "玫瑰", "content": "花语模块很实用，如果能支持按节日筛选花材就更好了。", "status": "processing", "reply_content": "收到，正在评估按节日和送礼场景做分类筛选。"},
]

async def seed_flowers():
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
    
    async with AsyncSessionFactory() as session:
        for d in data:
            result = await session.execute(select(Flower).filter(Flower.name == d["name"]))
            exists = result.scalars().first()
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
            session.add(row)
        await session.commit()
        print("Flowers seeded.")

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
                profile = UserProfile(
                    user_id=user.id,
                    nickname=user_data["nickname"],
                    bio=user_data["bio"],
                    avatar_url=user_data["avatar_url"],
                )
                session.add(profile)
                updated_profiles += 1
            else:
                profile.nickname = user_data["nickname"]
                profile.bio = user_data["bio"]
                profile.avatar_url = user_data["avatar_url"]
                updated_profiles += 1

        await session.commit()
        print(f"Seeded {created_count} user accounts and synced {updated_profiles} profiles.")


async def seed_comments_favorites_feedbacks():
    async with AsyncSessionFactory() as session:
        users = {
            user.username: user
            for user in (await session.execute(select(User))).scalars().all()
        }
        flowers = {
            flower.name: flower
            for flower in (await session.execute(select(Flower))).scalars().all()
        }
        feedback_columns = {
            column["name"]
            for column in await session.run_sync(
                lambda sync_session: inspect(sync_session.bind).get_columns("feedbacks")
            )
        }

        comment_count = 0
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
            if exists:
                continue

            session.add(
                Comment(
                    user_id=user.id,
                    flower_id=flower.id,
                    content=item["content"],
                    status=item["status"],
                )
            )
            comment_count += 1

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
                        select(Favorite).filter(
                            Favorite.user_id == user.id,
                            Favorite.flower_id == flower.id,
                        )
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
                    select(Feedback).filter(
                        Feedback.user_id == user.id,
                        Feedback.content == item["content"],
                    )
                )
            ).scalars().first()
            if exists:
                continue

            feedback_data = {
                "user_id": user.id,
                "content": item["content"],
                "status": item["status"],
            }
            if "flower_id" in feedback_columns:
                feedback_data["flower_id"] = flower.id if flower else None
            if "reply_content" in feedback_columns:
                feedback_data["reply_content"] = item["reply_content"]

            session.add(Feedback(**feedback_data))
            feedback_count += 1

        await session.commit()
        print(
            f"Seeded {comment_count} comments, {favorite_count} favorites, and {feedback_count} feedback entries."
        )

async def main():
    await seed_flowers()
    await seed_users()
    await seed_comments_favorites_feedbacks()

if __name__ == "__main__":
    asyncio.run(main())
