"""
app.py
Основной файл приложения для настройки Flask-приложения. Этот файл отвечает за создание и настройку экземпляра Flask,
подключение маршрутов и установку конфигурации приложения.
"""


from flask import Flask
from application.routes.user_routes import user_bp
from application.routes.agent_routes import agent_bp
from application.routes.chat_routes import chat_bp
from application.routes.session_routes import session_bp
import os


def create_app():
    """
    Создает и настраивает экземпляр Flask-приложения.
    """
    app = Flask(__name__, static_folder="../static")

    # Устанавливаем секретный ключ для сессий
    app.config["SECRET_KEY"] = os.urandom(24)

    # Регистрируем blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(session_bp)

    return app
