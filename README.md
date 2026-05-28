# Skincare Product Platform | 化妆品产品管理平台

化妆品行业的产品展示与管理系统。支持产品信息管理、多维标签分类、用户权限管理，适合美妆品牌内部产品开发团队使用。

## 功能特性

### 前台展示（公开）
- **新品速递** — 产品瀑布流展示，支持剂型/功效/功能三维筛选
- **产品详情** — 查看产品描述、成分列表、标签分类、多图展示
- **搜索** — 按名称、描述、成分模糊搜索

### 管理后台（管理员）
- **Dashboard** — 产品数、用户数、待审核用户等统计概览
- **产品管理** — 产品 CRUD，支持多标签选择（剂型/功效/功能）、多图上传、预览详情
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
| 数据库 | MySQL (PyMySQL) |
| 认证 | JWT (PyJWT) |
| 部署 | Docker Compose (多阶段构建) |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 22+
- MySQL 8.0+

### 1. 克隆项目

```bash
git clone https://github.com/yaowuya/skincare-home.git
cd skincare-home
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，修改 DATABASE_URL 等配置
```

### 3. 一键启动（推荐）

```bash
# 构建前端 + 启动 Flask（http://localhost:5000）
make dev
```

### 4. 分别启动（开发模式）

```bash
# 安装后端依赖
pip install -r requirements.txt

# 启动后端
python main.py

# 安装并启动前端（另一终端）
cd frontend
npm install
npm run dev
```

前端开发服务器运行在 `http://localhost:3000`，自动代理 `/api` 到后端 `:5000`。

### 5. 数据库迁移

```bash
# 应用迁移到数据库
flask db upgrade

# 模型变更后生成迁移脚本
flask db migrate -m "迁移说明"
```

### 6. 初始化数据

```bash
# 创建管理员账号
flask create-admin --username admin --email admin@test.com --password yourpassword

# 初始化功能分类标签
flask seed-tags
```

## Makefile 命令

| 命令 | 说明 |
|------|------|
| `make dev` | 一键启动：构建前端 + 启动后端 |
| `make build` | 构建前端并复制到 app/static |
| `make serve` | 启动 Flask 后端 |
| `make clean` | 清除构建产物 |
| `make install` | 安装前后端依赖 |
| `make test` | 运行后端测试 |
| `make migrate msg=描述` | 创建数据库迁移 |
| `make upgrade` | 执行数据库迁移 |
| `make admin USER=xx PASS=xx EMAIL=xx` | 创建管理员账号 |
| `make seed-tags` | 初始化默认标签 |

## Docker 部署

### 前置条件

- 已有可访问的 MySQL 数据库
- 在 `.env` 中配置 `DATABASE_URL`

### 部署命令

```bash
# 构建并启动
docker compose up -d --build

# 指定版本号构建
VERSION=1.0.0 docker compose up -d --build

# 查看日志
docker compose logs -f backend

# 停止
docker compose down
```

### 生产环境说明

- 镜像名：`skincare:${VERSION:-latest}`
- 使用 **多阶段构建**：Node 阶段构建 Vue SPA → Python 阶段打包到 Flask 镜像
- Flask 同时服务 API (`/api/*`) 和前端静态文件 (`/*`)，无需 Nginx
- 上传文件挂载到宿主机 `/data/skincare/uploads`
- 连接外部 MySQL 数据库（非 Docker 容器）
- Gunicorn 生产服务器，默认 4 workers

### 环境变量说明

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `DATABASE_URL` | ✅ | — | MySQL 连接串，格式：`mysql+pymysql://用户名:密码@主机:端口/数据库名` |
| `SECRET_KEY` | ✅ | — | Flask 密钥，生产环境请使用强随机值 |
| `JWT_SECRET` | 否 | 取 SECRET_KEY | JWT 签名密钥 |
| `JWT_EXPIRATION_HOURS` | 否 | 24 | JWT 令牌有效期（小时） |
| `ADMIN_USERNAME` | 否 | admin | 初始化管理员用户名 |
| `ADMIN_EMAIL` | 否 | admin@example.com | 初始化管理员邮箱 |
| `ADMIN_PASSWORD` | ✅ | — | 初始化管理员密码 |
| `GUNICORN_WORKERS` | 否 | 4 | Gunicorn 工作进程数 |
| `PORT` | 否 | 5000 | 宿主机映射端口 |

> **注意**：密码中如包含特殊字符（如 `@`、`#`），需进行 URL 编码（`@` → `%40`），否则 SQLAlchemy 解析连接串会出错。

## 运行测试

```bash
# 运行所有测试（使用 SQLite 内存数据库，无需 MySQL）
python -m pytest tests/ -v

# 运行单个测试文件
python -m pytest tests/test_auth.py -v

# 使用 Makefile
make test
```

当前测试覆盖：**58 个测试**，覆盖认证、用户管理、产品 CRUD、标签管理、文件上传。

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
├── docker-compose.yml
├── .dockerignore
├── entrypoint.sh         # 启动脚本（迁移 + Gunicorn）
├── Makefile              # 开发快捷命令
├── wsgi.py               # 生产入口
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
├── migrations/           # 数据库迁移
└── .env.example          # 环境变量示例
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

## License

MIT
