# PythonWeb

基于 **FastAPI + SQLModel** 构建的单体 Web 服务，提供用户认证、用户管理、物品管理等功能。

## 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI |
| ORM | SQLModel (SQLAlchemy + Pydantic) |
| 数据库 | PostgreSQL |
| 数据库迁移 | Alembic |
| 认证 | JWT (HS256) + OAuth2 Password Flow |
| 密码哈希 | pwdlib (Argon2 + bcrypt 双策略) |
| 邮件 | emails + Jinja2 |
| Python | >= 3.11 |

## 项目结构

```
PythonWeb/
├── app/
│   ├── core/               # 核心模块
│   │   ├── config.py       # 配置管理 (Settings)
│   │   ├── security.py     # JWT + 密码哈希
│   │   └── db.py           # 数据库引擎 + 初始数据
│   ├── api/
│   │   ├── deps.py         # 依赖注入 (Session / Token / CurrentUser)
│   │   ├── main.py         # API 路由注册
│   │   └── routes/         # 接口路由
│   │       ├── login.py    # 登录、密码重置
│   │       ├── users.py    # 用户 CRUD
│   │       ├── items.py    # 物品 CRUD
│   │       ├── utils.py    # 健康检查、测试邮件
│   │       └── private.py  # 本地私有接口
│   ├── alembic/            # 数据库迁移
│   ├── models.py           # 数据模型 + API Schema
│   ├── crud.py             # CRUD 操作
│   ├── utils.py            # 邮件工具
│   ├── initial_data.py     # 初始数据脚本
│   └── main.py             # 应用入口
├── db/
│   ├── schema.sql           # DDL 建表语句
│   ├── init_data.sql        # 初始数据 (超级用户)
│   ├── init_all.sql         # 一键初始化入口
│   └── generate_data_sql.py # 初始数据 SQL 生成器
├── scripts/
│   ├── start.bat           # Windows 启动脚本
│   └── start.sh            # Linux/macOS 启动脚本
├── tests/                  # 测试用例
├── pyproject.toml          # 项目元数据
├── requirements.txt        # 依赖列表
└── alembic.ini             # Alembic 配置
```

## 快速开始

### 1. 环境要求

- Python >= 3.11
- PostgreSQL

### 2. 创建 .env 文件

```env
# 环境
ENVIRONMENT=local

# 项目名称
PROJECT_NAME=PythonWeb

# 安全
SECRET_KEY=your-secret-key-at-least-32-chars

# 数据库
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=pythonweb

# 初始超级用户
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin123

# SMTP (可选，用于密码重置邮件)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

**方式一：Alembic 迁移 (推荐)**

```bash
# 创建数据库 (PostgreSQL)
createdb pythonweb

# 运行迁移
python -m alembic upgrade head

# 创建初始超级用户
python -m app.initial_data
```

**方式二：SQL 文件直接初始化**

```bash
# 创建数据库
createdb pythonweb

# 一键执行建表 + 插入初始数据
psql -U postgres -d pythonweb -f db/init_all.sql
```

或分步执行：

```bash
psql -U postgres -d pythonweb -f db/schema.sql    # 建表
psql -U postgres -d pythonweb -f db/init_data.sql  # 插入初始数据
```

**自定义初始用户 (SQL 方式)：**

```bash
# 重新生成 init_data.sql，指定自定义邮箱和密码
python db/generate_data_sql.py --email myadmin@test.com --password mypassword

# 然后执行 SQL
psql -U postgres -d pythonweb -f db/init_all.sql
```

### 5. 启动服务

**Windows:**
```bash
scripts\start.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

**或手动启动:**
```bash
export PYTHONPATH=.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. 访问

| 地址 | 说明 |
|------|------|
| http://localhost:8000/docs | Swagger API 文档 |
| http://localhost:8000/api/v1/openapi.json | OpenAPI Schema |
| http://localhost:8000/api/v1/utils/health-check/ | 健康检查 |

---

## API 接口

所有接口前缀为 `/api/v1`。

### 认证

| 方法 | 路径 | 认证 | 说明 |
|------|------|:--:|------|
| POST | `/login/access-token` | - | 登录获取 JWT Token (OAuth2 表单) |
| POST | `/login/test-token` | ✅ | 验证 Token 有效性 |
| POST | `/password-recovery/{email}` | - | 发送密码重置邮件 |

### 用户管理

| 方法 | 路径 | 认证 | 说明 |
|------|------|:--:|------|
| GET | `/users/` | 🔑 | 用户列表 (仅超级用户) |
| POST | `/users/` | 🔑 | 创建用户 (仅超级用户) |
| GET | `/users/me` | ✅ | 获取当前用户信息 |
| PATCH | `/users/me` | ✅ | 更新当前用户信息 |
| PATCH | `/users/me/password` | ✅ | 修改密码 |
| DELETE | `/users/me` | ✅ | 删除当前用户 |
| POST | `/users/signup` | - | 公开注册 |
| GET | `/users/{id}` | ✅ | 获取指定用户 |
| PATCH | `/users/{id}` | 🔑 | 更新指定用户 (仅超级用户) |
| DELETE | `/users/{id}` | 🔑 | 删除指定用户 (仅超级用户) |

### 物品管理

| 方法 | 路径 | 认证 | 说明 |
|------|------|:--:|------|
| GET | `/items/` | ✅ | 物品列表 (普通用户只看自己的) |
| POST | `/items/` | ✅ | 创建物品 |
| GET | `/items/{id}` | ✅ | 获取物品 (仅所有者或超级用户) |
| PUT | `/items/{id}` | ✅ | 更新物品 (仅所有者或超级用户) |
| DELETE | `/items/{id}` | ✅ | 删除物品 (仅所有者或超级用户) |

### 工具

| 方法 | 路径 | 认证 | 说明 |
|------|------|:--:|------|
| GET | `/utils/health-check/` | - | 健康检查 |
| POST | `/utils/test-email/` | 🔑 | 发送测试邮件 (仅超级用户) |

> ✅ 需登录 &emsp; 🔑 仅超级用户

---

## 鉴权流程

```
POST /login/access-token (username + password)
         │
         ▼
    JWT access_token
         │
         ▼
Authorization: Bearer <token>  ← 后续请求在 Header 中携带
         │
         ▼
 OAuth2PasswordBearer → 解码 JWT → 查数据库 → 返回 User 对象
```

### 获取 Token (curl)

```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
```

### 使用 Token (curl)

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <your-token>"
```

---

## 数据模型

### User

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| email | str | 邮箱 (唯一) |
| full_name | str? | 姓名 |
| hashed_password | str | 哈希密码 |
| is_active | bool | 是否激活 (默认 true) |
| is_superuser | bool | 是否超级用户 (默认 false) |
| created_at | datetime | 创建时间 (UTC) |

### Item

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| title | str | 标题 (1-255 字符) |
| description | str? | 描述 (1-255 字符) |
| owner_id | UUID | 所有者 (FK → user.id, 级联删除) |
| created_at | datetime | 创建时间 (UTC) |

---

## db/ 目录说明

不含 Alembic 的独立 SQL 脚本，可直接用 `psql` 初始化数据库。

| 文件 | 内容 |
|------|------|
| `schema.sql` | `user`、`item`、`alembic_version` 三张表，含索引、外键(级联删除)、注释 |
| `init_data.sql` | 插入 `admin@example.com` (Argon2 哈希密码) + 迁移版本记录 |
| `init_all.sql` | 入口文件，`\i` 依次执行 schema + init_data |
| `generate_data_sql.py` | 生成器，支持 `--email` `--password` 自定义初始用户 |

---

## 运行测试

```bash
pip install pytest httpx
set PYTHONPATH=.   # Windows
export PYTHONPATH=.  # Linux

python -m pytest tests/ -v
```

---

## 配置项

| 变量 | 默认值 | 说明 |
|------|------|------|
| `API_V1_STR` | `/api/v1` | API 前缀 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `11520` (8天) | Token 过期时间 |
| `SECRET_KEY` | 随机生成 | JWT 签名密钥 |
| `ENVIRONMENT` | `local` | 环境: local / staging / production |
| `BACKEND_CORS_ORIGINS` | `[]` | CORS 允许来源 |
| `FRONTEND_HOST` | `http://localhost:5173` | 前端地址 |
| `EMAIL_RESET_TOKEN_EXPIRE_HOURS` | `48` | 密码重置 Token 有效期 |
