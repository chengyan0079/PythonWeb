-- =============================================
-- PythonWeb 初始数据
-- 自动生成于: 2026-07-18 09:38:26 UTC
-- =============================================

-- -----------------------------------------
-- Alembic 版本记录 (标记迁移已完成)
-- -----------------------------------------
INSERT INTO alembic_version (version_num)
VALUES ('0001_initial')
ON CONFLICT (version_num) DO NOTHING;

-- -----------------------------------------
-- 初始超级用户
-- 邮箱: admin@example.com
-- 注意: 密码已使用 Argon2 + bcrypt 加密存储
-- -----------------------------------------
INSERT INTO "user" (id, email, is_active, is_superuser, full_name, hashed_password, created_at)
VALUES (
    'cb707457-c301-4966-856b-5c3b6c58915e',
    'admin@example.com',
    TRUE,
    TRUE,
    'Admin',
    '$argon2id$v=19$m=65536,t=3,p=4$ZUX51IeMcPLUaRLkF5MfXg$q5CTbsXSxXglYoxroRnomlnJZMxf33XOYMPfjOyokBM',
    '2026-07-18 09:38:26+00'
)
ON CONFLICT (email) DO NOTHING;
