import asyncio
import sys
import os
from sqlalchemy import text

# 将项目根目录添加到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.db import engine

async def fix_schema():
    async with engine.begin() as conn:
        print("开始检查并修复数据库表结构...")
        
        # 1. 修复 users 表
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN status ENUM('active', 'disabled') DEFAULT 'active'"))
            print("Successfully added status to users")
        except Exception as e:
            print(f"Skipped users.status: {e}")

        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN last_login_at DATETIME"))
            print("Successfully added last_login_at to users")
        except Exception as e:
            print(f"Skipped users.last_login_at: {e}")

        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN last_login_ip VARCHAR(64)"))
            print("Successfully added last_login_ip to users")
        except Exception as e:
            print(f"Skipped users.last_login_ip: {e}")

        # 2. 修复 flowers 表
        try:
            await conn.execute(text("ALTER TABLE flowers ADD COLUMN status ENUM('draft', 'pending', 'published') DEFAULT 'published'"))
            print("Successfully added status to flowers")
        except Exception as e:
            print(f"Skipped flowers.status: {e}")

        try:
            await conn.execute(text("ALTER TABLE flowers ADD COLUMN tags VARCHAR(256)"))
            print("Successfully added tags to flowers")
        except Exception as e:
            print(f"Skipped flowers.tags: {e}")

        # 3. 修复 recognition_records 表
        try:
            await conn.execute(text("ALTER TABLE recognition_records ADD COLUMN is_corrected BOOLEAN DEFAULT FALSE"))
            print("Successfully added is_corrected to recognition_records")
        except Exception as e:
            print(f"Skipped recognition_records.is_corrected: {e}")

        try:
            await conn.execute(text("ALTER TABLE recognition_records ADD COLUMN corrected_plant_id BIGINT"))
            await conn.execute(text("ALTER TABLE recognition_records ADD FOREIGN KEY (corrected_plant_id) REFERENCES flowers(id)"))
            print("Successfully added corrected_plant_id to recognition_records")
        except Exception as e:
            print(f"Skipped recognition_records.corrected_plant_id: {e}")

        # 4. 修复 comments 表
        try:
            await conn.execute(text("ALTER TABLE comments ADD COLUMN status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending'"))
            print("Successfully added status to comments")
        except Exception as e:
            print(f"Skipped comments.status: {e}")

        # 5. 修复 feedbacks 表 (扩充状态枚举)
        try:
            # MySQL 修改 ENUM 比较麻烦，先尝试增加列，如果已存在则尝试修改类型
            await conn.execute(text("ALTER TABLE feedbacks MODIFY COLUMN status ENUM('pending', 'processing', 'resolved', 'closed') DEFAULT 'pending'"))
            print("Successfully updated status enum for feedbacks")
        except Exception as e:
            print(f"Skipped feedbacks.status update: {e}")

        try:
            await conn.execute(text("ALTER TABLE feedbacks ADD COLUMN reply_content TEXT"))
            print("Successfully added reply_content to feedbacks")
        except Exception as e:
            print(f"Skipped feedbacks.reply_content: {e}")

        try:
            await conn.execute(text("ALTER TABLE feedbacks ADD COLUMN processed_at DATETIME"))
            print("Successfully added processed_at to feedbacks")
        except Exception as e:
            print(f"Skipped feedbacks.processed_at: {e}")

        print("数据库结构修复完成！")

if __name__ == "__main__":
    asyncio.run(fix_schema())
