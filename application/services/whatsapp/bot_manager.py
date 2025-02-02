# """
# bot_manager.py
# Модуль для управления жизненным циклом WhatsApp-ботов через Twilio API.
# """
#
# import asyncio
# from application.services.whatsapp.runner import WhatsAppBotRunner
# from utils.logs.logger import logger
#
#
# class WhatsAppBotManager:
#     def __init__(self):
#         """
#         Инициализация менеджера ботов.
#         Создаётся словарь для хранения запущенных ботов по session_id.
#         """
#         self.bots = {}
#
#     async def start_bot(self, session_id, phone_number):
#         """
#         Асинхронный запуск бота WhatsApp по session_id и номеру телефона.
#
#         :param session_id: Идентификатор сессии
#         :param phone_number: Номер телефона, подключённый к Twilio
#         """
#         if session_id in self.bots:
#             logger.log(f"Бот {session_id} уже запущен", "INFO")
#             return
#
#         bot_runner = WhatsAppBotRunner(session_id, phone_number)
#         self.bots[session_id] = bot_runner
#
#         try:
#             await bot_runner.start_webhook()
#             logger.log(f"Бот WhatsApp сессии {session_id} успешно запущен.", "INFO")
#         except Exception as e:
#             logger.log(f"Ошибка запуска бота {session_id}: {e}", "ERROR")
#
#     async def stop_bot(self, session_id):
#         """
#         Асинхронная остановка бота WhatsApp по session_id.
#
#         :param session_id: Идентификатор сессии
#         """
#         if session_id not in self.bots:
#             logger.log(f"Бот для сессии {session_id} не найден.", "WARNING")
#             return
#
#         bot_runner = self.bots.pop(session_id)
#
#         await bot_runner.stop_webhook()
#         logger.log(f"Бот сессии {session_id} остановлен.", "INFO")
#
#     async def start_all_bots(self, sessions):
#         """
#         Запуск всех активных WhatsApp-сессий.
#         """
#         tasks = []
#         for session in sessions:
#             session_id = session['id']
#             phone_number = session['phone_number']
#             tasks.append(self.start_bot(session_id, phone_number))
#
#         await asyncio.gather(*tasks)
#         logger.log("Все боты WhatsApp запущены.", "INFO")
#
#     async def stop_all_bots(self):
#         """
#         Остановка всех запущенных WhatsApp-сессий.
#         """
#         tasks = [self.stop_bot(session_id) for session_id in list(self.bots.keys())]
#         await asyncio.gather(*tasks)
#         logger.log("Все боты WhatsApp остановлены.", "INFO")
#
#     def get_bot(self, session_id):
#         """
#         Получение бота WhatsApp по session_id.
#
#         :param session_id: Идентификатор сессии
#         :return: Экземпляр бота или None
#         """
#         return self.bots.get(session_id)
#
#
# # Создание экземпляра менеджера ботов
# whatsapp_bot_manager = WhatsAppBotManager()
