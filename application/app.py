from flask import Flask
from application.routes import main  # Импортируем основное блюпринт с маршрутами
import os


def create_app():
    app = Flask(__name__, static_folder='../static')
    app.config['SECRET_KEY'] = os.urandom(24)  # Секретный ключ для сессий
    app.register_blueprint(main)  # Подключаем маршруты
    return app
