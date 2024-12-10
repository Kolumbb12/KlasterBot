"""
bot_manager.py
Модуль для управления жизненным циклом ботов в системе. Этот файл содержит класс `BotManager`, который отвечает за
запуск, остановку и управление ботами на основе сессий. Он предоставляет методы для асинхронного старта и остановки
ботов, а также обработки нескольких ботов одновременно.

Основные функции:
- `start_bot(session_id, token, port)`: Запускает бота для указанной сессии, если он ещё не запущен.
Использует класс `BotRunner` для выполнения старта бота и его webhook.
- `stop_bot(session_id)`: Останавливает бота для указанной сессии, завершив его webhook.
- `start_all_bots(sessions)`: Запускает все боты для списка сессий асинхронно.
- `stop_all_bots()`: Останавливает все боты.
- `get_bot(session_id)`: Возвращает экземпляр бота для указанной сессии.

Этот модуль используется для централизованного управления ботов в приложении, обеспечивая возможность асинхронной
работы с множеством ботов и их настройки.
"""

import asyncio
from application.services.telegram.runner import BotRunner
from utils.logs.logger import logger


class BotManager:

    def __init__(self):
        self.bots = {}

    async def start_bot(self, session_id, token, port):
        """
        Асинхронный запуск бота по session_id, token и port.
        """
        if session_id in self.bots:
            print(f"Бот {session_id} уже запущен.")
            return

        bot_runner = BotRunner(session_id, token, port)
        self.bots[session_id] = bot_runner
        try:
            await bot_runner.start_webhook()
            logger.log(f"Бот {session_id} успешно запущен")
        except Exception as e:
            logger.log(f"Бот {session_id} не запущен, ошибка: {e}", "ERROR")


    async def stop_bot(self, session_id):
        """
        Асинхронная остановка бота по session_id.
        """
        if session_id not in self.bots:
            print(f"Бот для сессии {session_id} не запущен.")
            return

        bot_runner = self.bots.pop(session_id)

        await bot_runner.stop_webhook()
        print(f"Бот для сессии {session_id} остановлен.")

    async def start_all_bots(self, sessions):
        """
        Асинхронный запуск всех активных ботов (сессий).
        """
        tasks = []
        for session in sessions:
            session_id = session['id']
            token = session['api_token']
            port = 5001 + session_id
            tasks.append(self.start_bot(session_id, token, port))
        await asyncio.gather(*tasks)

    async def stop_all_bots(self):
        """
        Асинхронная остановка всех запущенных ботов.
        """
        tasks = [self.stop_bot(session_id) for session_id in self.bots.keys()]
        await asyncio.gather(*tasks)

    def get_bot(self, session_id):
        """
        Возвращает экземпляр бота.
        """
        return self.bots.get(session_id)


bot_manager = BotManager()
