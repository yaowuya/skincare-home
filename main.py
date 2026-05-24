"""
开发服务器入口。
生产环境使用 wsgi.py + Gunicorn 启动。
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
