.PHONY: help dev build serve clean test

# 项目根目录
ROOT := $(shell pwd)
VENV   := $(ROOT)/venv/Scripts
PIP    := $(VENV)/pip
PYTHON := $(VENV)/python
FLASK  := $(VENV)/flask
NPM    := npm

# 前后端目录
FRONTEND_DIR  := $(ROOT)/frontend
STATIC_DIR    := $(ROOT)/app/static
DIST_DIR      := $(FRONTEND_DIR)/dist

help: ## 显示帮助信息
	@echo ""
	@echo "可用命令:"
	@echo "  make dev      - 一键启动：构建前端 + 启动后端（本地调试验证）"
	@echo "  make build    - 构建前端并将静态文件复制到 app/static"
	@echo "  make serve    - 启动 Flask 后端（需先 make build）"
	@echo "  make clean    - 清除前端构建产物和 app/static"
	@echo "  make install  - 安装前后端依赖"
	@echo "  make test     - 运行后端测试"
	@echo ""

# ========== 一键开发验证 ==========

dev: build serve ## 一键启动：构建前端 + 启动后端（本地调试验证）

# ========== 前端构建 ==========

build: ## 构建前端并将静态文件复制到 app/static
	@echo ">>> 构建前端..."
	cd $(FRONTEND_DIR) && $(NPM) run build
	@echo ">>> 复制静态文件到 app/static..."
	@rm -rf $(STATIC_DIR)
	@cp -r $(DIST_DIR) $(STATIC_DIR)
	@echo ">>> 构建完成！静态文件已部署到 app/static"
	@echo ">>> 执行 make serve 启动后端访问 http://localhost:5000"

# ========== 后端启动 ==========

serve: ## 启动 Flask 后端（需先 make build）
	@echo ">>> 启动 Flask 开发服务器 http://localhost:5000"
	$(PYTHON) main.py

# ========== 清理 ==========

clean: ## 清除前端构建产物和 app/static
	@echo ">>> 清除构建产物..."
	@rm -rf $(STATIC_DIR)
	@rm -rf $(DIST_DIR)
	@echo ">>> 清除完成"

# ========== 依赖安装 ==========

install: ## 安装前后端依赖
	@echo ">>> 安装后端依赖..."
	$(PIP) install -r requirements.txt
	@echo ">>> 安装前端依赖..."
	cd $(FRONTEND_DIR) && $(NPM) install
	@echo ">>> 依赖安装完成"

# ========== 测试 ==========

test: ## 运行后端测试
	$(PYTHON) -m pytest tests/ -v

# ========== 数据库迁移 ==========

migrate: ## 创建数据库迁移
	$(FLASK) db migrate -m "$(msg)"

upgrade: ## 执行数据库迁移
	$(FLASK) db upgrade

# ========== 管理员账号 ==========

admin: ## 创建管理员账号（需传参: make admin USER=xxx PASS=xxx EMAIL=xxx）
	$(FLASK) create-admin --username $(USER) --email $(EMAIL) --password $(PASS)

seed-tags: ## 初始化默认标签
	$(FLASK) seed-tags
