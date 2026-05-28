#!/bin/sh
set -e

# 等待外部数据库就绪（最多 60 秒）
echo "Waiting for database..."
for i in $(seq 1 30); do
  if python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.environ['DATABASE_URL'])
conn = engine.connect()
conn.close()
" 2>/dev/null; then
    echo "Database ready."
    break
  fi
  if [ "$i" = "30" ]; then
    echo "ERROR: Database not available after 60s, aborting."
    exit 1
  fi
  sleep 2
done

# 执行数据库迁移
flask db upgrade

# 初始化默认标签（幂等，重复执行不会报错）
flask seed-tags 2>/dev/null || true

# 创建管理员账号（已存在则跳过）
flask create-admin \
  --username "${ADMIN_USERNAME:-admin}" \
  --email "${ADMIN_EMAIL:-admin@example.com}" \
  --password "${ADMIN_PASSWORD:?ADMIN_PASSWORD not set in .env}" \
  2>/dev/null || true

# 启动 Gunicorn
exec gunicorn \
  --workers "${GUNICORN_WORKERS:-4}" \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  wsgi:app
