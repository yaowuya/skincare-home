# Skincare Product Platform | 化妆品产品管理平台

化妆品行业的产品展示与管理系统。支持产品信息管理、多维标签分类、用户权限管理，适合美妆品牌内部产品开发团队使用。

## 功能特性

### 前台展示（公开）
- **新品速递** — 产品瀑布流展示，支持剂型/功效/功能三维筛选
- **产品详情** — 查看产品描述、成分列表、标签分类
- **搜索** — 按名称、描述、成分模糊搜索

### 管理后台（管理员）
- **Dashboard** — 产品数、用户数、待审核用户等统计概览
- **产品管理** — 产品 CRUD，支持多标签选择（剂型/功效/功能）、图片上传
- **用户管理** — 用户 CRUD、注册审核、角色分配
- **标签管理** — 自定义剂型/功效/功能三类标签

### 用户角色
- **管理员** — 产品上传/编辑/删除、用户管理、标签管理
- **普通用户** — 查看产品、搜索（需管理员审核通过）

## 技术栈

| 层 | 技术 |
|------|---------|
| 前端 | Vue 3 + Element Plus + Pinia + Vue Router |
| 后端 | Flask + Flask-RESTx + SQLAlchemy |
| 数据库 | PostgreSQL 16 |
| 认证 | JWT (PyJWT) |
| 部署 | Docker Compose (腾讯云) |

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 20+
- PostgreSQL 16（开发可用 Docker 替代）

### 1. 克隆项目

```bash
git clone https://github.com/yaowuya/skincare-home.git
cd skincare-home
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 修改数据库连接等配置
```

### 3. 启动后端

```bash
# 创建虚拟环境（如有）
python -m venv venv

# 安装依赖
./venv/Scripts/pip install -r requirements.txt

# 启动开发服务器
./venv/Scripts/flask --app "app:create_app()" run --reload
```

### 4. 启动前端（开发模式）

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器运行在 `http://localhost:3000`，自动代理 `/api` 到后端 `:5000`。

### 5. 初始化

```bash
# 创建管理员账号
./venv/Scripts/flask create-admin --username admin --email admin@test.com --password yourpassword

# 初始化功能分类标签
./venv/Scripts/flask seed-tags
```

## Docker 部署

```bash
# 构建并启动
docker compose up -d --build

# 查看日志
docker compose logs -f backend

# 停止
docker compose down
```

生产环境使用 **多阶段构建**：
1. Node 阶段构建 Vue SPA
2. Python 阶段打包到 Flask 镜像中
3. Flask 同时服务 API 和前端静态文件（无需 Nginx）

## 运行测试

```bash
# 运行所有测试（使用 SQLite 内存数据库，无需 PostgreSQL）
./venv/Scripts/python -m pytest tests/ -v

# 运行单个测试文件
./venv/Scripts/python -m pytest tests/test_auth.py -v

# 运行单个测试用例
./venv/Scripts/python -m pytest tests/test_auth.py::TestLogin::test_login_success -v
```

当前测试覆盖：**56 个测试**，覆盖认证、用户管理、产品 CRUD、标签管理、文件上传。

## 项目结构

```
skincare-home/
├── app/                  # Flask 应用
│   ├── api/              # REST API 命名空间
│   │   ├── auth.py       # 注册/登录/密码修改
│   │   ├── users.py      # 用户管理（管理员）
│   │   ├── products.py   # 产品 CRUD + 搜索/分页
│   │   └── tags.py       # 标签管理（3 类）
│   ├── auth/             # JWT 认证装饰器
│   ├── models/           # SQLAlchemy 模型
│   ├── utils/            # 工具函数（文件上传等）
│   ├── cli.py            # Flask CLI 命令
│   └── __init__.py       # App 工厂
├── config.py             # 配置（从 .env 读取）
├── requirements.txt
├── Dockerfile            # 多阶段构建
├── entrypoint.sh         # 启动脚本
├── frontend/             # Vue 3 前端
│   └── src/
│       ├── api/          # Axios + API 模块
│       ├── store/        # Pinia 状态管理
│       ├── router/       # 路由 + JWT 守卫
│       ├── views/
│       │   ├── public/   # 产品展示页
│       │   └── admin/    # 管理后台
│       └── components/   # 共享组件
├── tests/                # 后端测试
├── docker-compose.yml
└── .env.example
```

## API 概览

| 模块 | 端点 | 鉴权 | 说明 |
|------|------|------|------|
| Auth | `POST /api/auth/register` | 无 | 用户注册 |
| Auth | `POST /api/auth/login` | 无 | 登录获取 JWT |
| Auth | `GET /api/auth/me` | JWT | 当前用户信息 |
| Auth | `PUT /api/auth/password` | JWT | 修改密码 |
| Users | `GET/POST /api/users/` | 管理员 | 用户列表/创建 |
| Users | `PUT/DELETE /api/users/<id>` | 管理员 | 编辑/删除用户 |
| Users | `POST /api/users/<id>/approve` | 管理员 | 审核用户 |
| Products | `GET /api/products/` | 无 | 产品列表（搜索/分页/筛选） |
| Products | `GET /api/products/<id>` | 无 | 产品详情 |
| Products | `POST /api/products/` | 管理员 | 创建产品 |
| Products | `PUT/DELETE /api/products/<id>` | 管理员 | 编辑/删除产品 |
| Products | `POST/DELETE /api/products/<id>/image` | 管理员 | 产品图片上传/删除 |
| Tags | `GET /api/tags/<type>` | 无 | 标签列表（type: form/effect/function） |
| Tags | `POST/PUT/DELETE /api/tags/<type>/<id>` | 管理员 | 标签 CRUD |

## 设计文档

- [系统设计 Spec](docs/superpowers/specs/2026-05-24-admin-management-design.md)
- [实施计划](docs/superpowers/plans/)

## License

MIT
