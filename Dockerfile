# ============================================================
# Stage 1: 构建 Vue 前端
# ============================================================
FROM node:22-alpine AS frontend

WORKDIR /app

# 使用淘宝 NPM 镜像加速
RUN npm config set registry https://registry.npmmirror.com

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ============================================================
# Stage 2: Python 后端 + 前端静态文件
# ============================================================
FROM python:3.11-slim

WORKDIR /app

# 使用阿里云 PyPI 镜像加速
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set global.trusted-host mirrors.aliyun.com

# 系统依赖（netcat 用于 entrypoint 等待 PostgreSQL）
RUN apt-get update \
    && apt-get install -y --no-install-recommends netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY app/ ./app/
COPY config.py wsgi.py main.py ./
COPY migrations/ ./migrations/
COPY entrypoint.sh ./

# 从 Stage 1 复制前端构建产物
COPY --from=frontend /app/dist ./app/static

RUN chmod +x entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
