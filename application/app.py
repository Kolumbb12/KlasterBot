"""
app.py
Основной файл приложения для настройки Flask-приложения. Этот файл отвечает за создание и настройку экземпляра Flask,
подключение маршрутов и установку конфигурации приложения.
"""

from flask import Flask, session, jsonify, request
from application.routes.user_routes import user_bp
from application.routes.agent_routes import agent_bp
from application.routes.chat_routes import chat_bp
from application.routes.session_routes import session_bp
from utils.access_control import limiter
import os


def create_app():
    """
    Создает и настраивает экземпляр Flask-приложения.
    """
    app = Flask(__name__, static_folder="../static")

    # Устанавливаем секретный ключ для сессий
    app.config["SECRET_KEY"] = os.urandom(24)

    # Применяем Limiter к приложению
    limiter.init_app(app)


    # Регистрируем blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(session_bp)

    @app.errorhandler(429)
    def ratelimit_error(e):
        """
        Обработчик ошибки 429 (Too Many Requests).
        Возвращает JSON-ответ с корректной кодировкой без экранирования Unicode-символов.
        """
        return jsonify(error="There are too many requests. Please wait.", description=str(e)), 429

    return app
