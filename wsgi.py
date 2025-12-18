"""
WSGI entrypoint для развертывания на продакшене
Использование с Gunicorn: gunicorn wsgi:app
"""
from app import app

if __name__ == "__main__":
    app.run()

