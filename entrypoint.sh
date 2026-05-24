#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do sleep 1; done
echo "PostgreSQL ready."

flask db upgrade
flask seed-tags
flask create-admin --username admin --email admin@example.com --password admin123 2>/dev/null || true

exec gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
