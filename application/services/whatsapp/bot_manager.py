"""
bot_manager.py
Модуль для управления жизненным циклом WhatsApp-ботов через Selenium.

Этот модуль:
- Запускает WhatsApp Web через Selenium
- Ожидает авторизацию пользователя
- Настраивает вебхук для получения сообщений
- Обрабатывает входящие сообщения и отвечает через GPT API
"""

# import asyncio
# from application.services.whatsapp.runner import WhatsAppWebRunner
# from database.db_functions import get_last_webhook_port, get_webhook_port
# from utils.logs.logger import logger
# from dotenv import load_dotenv
# import os
#
#
# load_dotenv()
#
#
# class WhatsAppBotManager:
#     def __init__(self):
#         self.bots = {}
#
#     async def start_bot(self, session_id, phone_number):
#         """
#         Запуск WhatsApp Web бота.
#         """
#         if session_id in self.bots:
#             logger.log(f"Бот {session_id} уже запущен", "INFO")
#             return
#
#         webhook_port = get_last_webhook_port()
#         webhook_url = f"{os.getenv('NGROK_ADDRESS')}/webhook/{session_id}"
#
#         bot_runner = WhatsAppWebRunner(session_id, phone_number, webhook_url)
#         self.bots[session_id] = bot_runner
#
#         await bot_runner.start()
#
#     async def stop_bot(self, session_id):
#         """
#         Остановка WhatsApp Web бота.
#         """
#         if session_id not in self.bots:
#             logger.log(f"Бот для сессии {session_id} не найден.", "WARNING")
#             return
#
#         bot_runner = self.bots.pop(session_id)
#         await bot_runner.stop()
#         logger.log(f"Бот сессии {session_id} остановлен.", "INFO")
#
#     async def start_all_bots(self, sessions):
#         """
#         Асинхронный запуск всех активных ботов (сессий).
#         """
#         tasks = [self.start_bot(session['id'], session['bot_username']) for session in sessions]
#         await asyncio.gather(*tasks)
#
#     async def stop_all_bots(self):
#         """
#         Асинхронная остановка всех запущенных ботов.
#         """
#         tasks = [self.stop_bot(session_id) for session_id in self.bots.keys()]
#         await asyncio.gather(*tasks)
#
#     def get_bot(self, session_id):
#         return self.bots.get(session_id)
#
#
# whatsapp_bot_manager = WhatsAppBotManager()


from application.services.whatsapp.session_manager import WhatsAppSessionManager
from application.services.whatsapp.whatsapp_session import WhatsAppSession


class WhatsAppBotManager:
    """Класс для управления всеми запущенными сессиями BAS."""

    def __init__(self):
        self.sessions = {}
        self.manager = WhatsAppSessionManager()

    def start_bot(self, session_id, phone_number):
        """Запускает новый BAS-бот для указанной сессии."""
        if session_id in self.sessions:
            print(f"Бот {session_id} уже запущен.")
            return

        session = WhatsAppSession(session_id, phone_number, self.manager)
        session.start()
        self.sessions[session_id] = session

    def stop_bot(self, session_id):
        """Останавливает BAS-бота."""
        if session_id not in self.sessions:
            print(f"Сессия {session_id} не найдена.")
            return

        session = self.sessions.pop(session_id)
        session.stop()

    def stop_all_bots(self):
        """Останавливает все запущенные сессии."""
        for session_id in list(self.sessions.keys()):
            self.stop_bot(session_id)

    def get_bot(self, session_id):
        """Возвращает объект сессии по ID."""
        return self.sessions.get(session_id)


whatsapp_bot_manager = WhatsAppBotManager()
