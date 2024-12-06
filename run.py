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

from application.app import create_app
from database.db_connection import db_instance
from utils.logs.logger import logger
from application.services.telegram.bot_manager import bot_manager
from database.db_functions import get_all_active_sessions
import asyncio
import threading
import atexit


# Создаем Flask-приложение
flask_app = create_app()

# Главный событийный цикл asyncio
main_event_loop = asyncio.new_event_loop()
flask_app.config["event_loop"] = main_event_loop

# Регистрация функции завершения соединения с базой
atexit.register(db_instance.teardown)


async def start_all_bots():
    """
    Асинхронный запуск всех активных ботов.
    """
    active_sessions = get_all_active_sessions()
    await bot_manager.start_all_bots(active_sessions)


def run_flask():
    """
    Запуск Flask в отдельном потоке.
    """
    flask_app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    try:
        # Запускаем всех активных ботов в главном цикле событий
        asyncio.run_coroutine_threadsafe(start_all_bots(), main_event_loop)

        # Запускаем Flask в отдельном потоке
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.start()

        # Запускаем основной событийный цикл
        main_event_loop.run_forever()
    except Exception as e:
        logger.log(f"Ошибка при запуске ботов или Flask: {e}", "ERROR")
