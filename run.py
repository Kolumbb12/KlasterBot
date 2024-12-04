"""
run.py
Этот файл является точкой входа для запуска Flask-приложения. Он инициализирует приложение с использованием функции
`create_app` из модуля `application.app` и запускает сервер. Также здесь предусмотрено автоматическое завершение
соединения с базой данных при завершении работы приложения.

Основные компоненты:
1. Инициализация Flask-приложения с использованием функции `create_app`.
2. Настройка запуска сервера в режиме отладки (debug=True).
3. Регистрация функции завершения соединения с базой данных с помощью модуля `atexit`,
чтобы гарантировать корректное завершение соединения.
"""

import asyncio
from application.app import create_app
from database.db_connection import db_instance
import atexit
from application.services.telegram.bot_manager import bot_manager
from utils.logs.logger import logger


# Инициализация Flask-приложения
app = create_app()


def start_bot_manager():
    """
    Запускает все активные боты в потоках.
    """
    try:
        bot_manager.start_all_bots()
        logger.log("Все активные боты запущены.")
    except Exception as e:
        logger.log(f"Ошибка при запуске ботов: {e}", "ERROR")


# Регистрируем функцию завершения через atexit
atexit.register(db_instance.teardown)
atexit.register(bot_manager.stop_all_bots)  # Остановка ботов при завершении Flask


# Запуск сервера
if __name__ == '__main__':
    # Запускаем ботов до старта Flask
    start_bot_manager()
    app.run(debug=True, use_reloader=False)
