-- =============================================
-- PythonWeb Database Schema
-- PostgreSQL DDL
-- =============================================

-- 创建扩展 (如果需要)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------
-- 1. 用户表 (user)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS "user" (
    id              UUID                     NOT NULL,
    email           VARCHAR(255)             NOT NULL,
    is_active       BOOLEAN                  NOT NULL DEFAULT TRUE,
    is_superuser    BOOLEAN                  NOT NULL DEFAULT FALSE,
    full_name       VARCHAR(255),
    hashed_password VARCHAR                  NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
    CONSTRAINT pk_user PRIMARY KEY (id)
);

-- 邮箱唯一索引
CREATE UNIQUE INDEX IF NOT EXISTS ix_user_email ON "user" (email);

-- 用户表注释
COMMENT ON TABLE "user" IS '用户表';
COMMENT ON COLUMN "user".id IS '用户唯一标识 (UUID)';
COMMENT ON COLUMN "user".email IS '邮箱地址';
COMMENT ON COLUMN "user".is_active IS '是否激活';
COMMENT ON COLUMN "user".is_superuser IS '是否超级管理员';
COMMENT ON COLUMN "user".full_name IS '用户姓名';
COMMENT ON COLUMN "user".hashed_password IS '加密后的密码 (Argon2/bcrypt)';
COMMENT ON COLUMN "user".created_at IS '创建时间 (UTC)';


-- -----------------------------------------
-- 2. 物品表 (item)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS "item" (
    id          UUID                     NOT NULL,
    title       VARCHAR(255)             NOT NULL,
    description VARCHAR(255),
    owner_id    UUID                     NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
    CONSTRAINT pk_item PRIMARY KEY (id),
    CONSTRAINT fk_item_owner FOREIGN KEY (owner_id)
        REFERENCES "user" (id) ON DELETE CASCADE
);

-- 物品表注释
COMMENT ON TABLE "item" IS '物品表';
COMMENT ON COLUMN "item".id IS '物品唯一标识 (UUID)';
COMMENT ON COLUMN "item".title IS '物品标题';
COMMENT ON COLUMN "item".description IS '物品描述';
COMMENT ON COLUMN "item".owner_id IS '所有者用户ID';
COMMENT ON COLUMN "item".created_at IS '创建时间 (UTC)';


-- -----------------------------------------
-- 3. Alembic 迁移版本记录表
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT pk_alembic_version PRIMARY KEY (version_num)
);

COMMENT ON TABLE alembic_version IS 'Alembic 数据库迁移版本记录';
