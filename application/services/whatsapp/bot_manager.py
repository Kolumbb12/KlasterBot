"""
bot_manager.py
Модуль для управления жизненным циклом WhatsApp-ботов через BAS.
"""

import asyncio
from application.services.whatsapp.session_manager import WhatsAppSessionManager
from application.services.whatsapp.whatsapp_session import WhatsAppSession
from utils.logs.logger import logger


class WhatsAppBotManager:
    """Асинхронный менеджер для управления WhatsApp-сессиями."""

    def __init__(self):
        self.sessions = {}
        self.manager = WhatsAppSessionManager()

    async def start_bot(self, session_id, phone_number):
        """Асинхронно запускает нового BAS-бота."""
        if session_id in self.sessions:
            print(f"Бот {session_id} уже запущен.")
            return

        session = WhatsAppSession(session_id, phone_number, self.manager)

        # Запускаем бота в отдельной асинхронной задаче
        task = asyncio.create_task(session.start_async())
        self.sessions[session_id] = task

        try:
            await task
            logger.log(f"WhatsApp бот {session_id} успешно запущен", "INFO")
        except Exception as e:
            logger.log(f"Ошибка запуска бота {session_id}: {e}", "ERROR")

    async def stop_bot(self, session_id):
        """Асинхронно останавливает BAS-бота."""
        if session_id not in self.sessions:
            print(f"Сессия {session_id} не найдена.")
            return

        task = self.sessions.pop(session_id)
        task.cancel()
        logger.log(f"WhatsApp бот {session_id} остановлен", "INFO")

    async def stop_all_bots(self):
        """Асинхронно останавливает все сессии."""
        tasks = [self.stop_bot(session_id) for session_id in self.sessions.keys()]
        await asyncio.gather(*tasks)

    def get_bot(self, session_id):
        """Возвращает объект задачи бота по ID."""
        return self.sessions.get(session_id)


whatsapp_bot_manager = WhatsAppBotManager()
