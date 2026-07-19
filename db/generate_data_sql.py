"""
生成初始数据 SQL 文件 (包含加密后的密码哈希)

用法:
    python db/generate_data_sql.py
    python db/generate_data_sql.py --email admin@example.com --password admin123
"""
import argparse
import sys
import os
import uuid
from datetime import UTC, datetime

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash


TEMPLATE = """-- =============================================
-- PythonWeb 初始数据
-- 自动生成于: {generated_at}
-- =============================================

-- -----------------------------------------
-- Alembic 版本记录 (标记迁移已完成)
-- -----------------------------------------
INSERT INTO alembic_version (version_num)
VALUES ('0001_initial')
ON CONFLICT (version_num) DO NOTHING;

-- -----------------------------------------
-- 初始超级用户
-- 邮箱: {email}
-- 注意: 密码已使用 Argon2 + bcrypt 加密存储
-- -----------------------------------------
INSERT INTO "user" (id, email, is_active, is_superuser, full_name, hashed_password, created_at)
VALUES (
    '{user_id}',
    '{email}',
    TRUE,
    TRUE,
    'Admin',
    '{hashed_password}',
    '{created_at}'
)
ON CONFLICT (email) DO NOTHING;
"""


def main():
    parser = argparse.ArgumentParser(description="生成初始数据 SQL 文件")
    parser.add_argument(
        "--email",
        default="admin@example.com",
        help="超级用户邮箱 (默认: admin@example.com)",
    )
    parser.add_argument(
        "--password",
        default="admin123",
        help="超级用户密码 (默认: admin123)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="输出文件路径 (默认: db/init_data.sql)",
    )
    args = parser.parse_args()

    # 生成密码哈希
    hashed_password = get_password_hash(args.password)

    # 生成固定 UUID 和当前时间
    user_id = uuid.uuid4()
    created_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S+00")
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    # 填充模板
    sql_content = TEMPLATE.format(
        generated_at=generated_at,
        email=args.email,
        user_id=str(user_id),
        hashed_password=hashed_password,
        created_at=created_at,
    )

    # 输出
    output_path = args.output or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "init_data.sql"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sql_content)

    print(f"Generated: {output_path}")
    print(f"  User: {args.email}")
    print(f"  UUID: {user_id}")


if __name__ == "__main__":
    main()
