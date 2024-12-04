import asyncio
import threading
from application.services.telegram.runner import start_telegram_bot, stop_telegram_bot
from database.db_functions import get_all_active_sessions
from aiogram import Bot, Dispatcher
from utils.logs.logger import logger


class BotManager:

    def __init__(self):
        self.active_bots = {}  # Словарь: session_id -> (thread, loop, bot, dp)
        self.stop_flags = {}  # Словарь: session_id -> флаг состояния бота

    def start_bot(self, session_id, api_token):
        if session_id in self.active_bots:
            logger.log(f"Бот для сессии {session_id} уже запущен.")
            return

        # Создаем флаг остановки
        self.stop_flags[session_id] = {"stop": False}

        def run_bot():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Создаем bot и dp внутри потока
            bot = Bot(token=api_token)
            dp = Dispatcher()

            # Сохраняем поток, loop, bot и dp
            self.active_bots[session_id] = (thread, loop, bot, dp)

            # Запускаем Telegram бота с флагом
            loop.run_until_complete(start_telegram_bot(session_id, bot, dp, self.stop_flags[session_id]))

        logger.log(f"Создание потока для бота сессии {session_id}")
        try:
            thread = threading.Thread(target=run_bot, daemon=True)
            thread.start()
            logger.log(f"Поток для бота сессии {session_id} добавлен в active_bots")
        except Exception as e:
            logger.log(f"Ошибка при запуске Telegram бота для сессии {session_id}: {e}", "ERROR")

    def stop_bot(self, session_id):
        """
        Останавливает Telegram бота.
        """
        if session_id not in self.active_bots:
            logger.log(f"Бот для сессии {session_id} не запущен.", "WARNING")

        logger.log(f"Попытка остановить бота для сессии {session_id}")
        thread, loop, bot, dp = self.active_bots.pop(session_id)

        # Устанавливаем флаг остановки
        self.stop_flags[session_id]["stop"] = True

        try:
            # Завершаем асинхронную задачу через loop
            future = asyncio.run_coroutine_threadsafe(
                stop_telegram_bot(session_id, bot, dp, self.stop_flags[session_id]),
                loop,
            )
            future.result(timeout=5)  # Таймаут на завершение корутины

            logger.log(f"Polling для бота сессии {session_id} завершён.")
        except Exception as e:
            logger.log(f"Ошибка при остановке Telegram бота для сессии {session_id}: {e}", "ERROR")

        # Закрываем loop
        try:
            loop.call_soon_threadsafe(loop.stop)
            loop.close()
            logger.log(f"Event loop для бота сессии {session_id} закрыт.")
        except Exception as e:
            logger.log(f"Ошибка при закрытии event loop: {e}", "ERROR")

        # Принудительное завершение потока
        if thread.is_alive():
            thread.join(timeout=5)  # Таймаут для завершения потока
            if thread.is_alive():
                logger.log(f"Поток для бота сессии {session_id} не завершен.", "WARNING")
            else:
                logger.log(f"Поток для бота сессии {session_id} завершён.")
        else:
            logger.log(f"Поток для бота сессии {session_id} уже завершён.")

    def start_all_bots(self):
        """
        Запускает всех активных ботов из базы данных.
        """
        logger.log("Начало запуска всех ботов...")
        sessions = get_all_active_sessions()  # Получаем список активных сессий
        if not sessions:
            logger.log("Нет активных сессий для запуска.", "WARNING")
            return

        for session in sessions:
            session_id = session['id']
            api_token = session['api_token']

            if session_id in self.active_bots:
                logger.log(f"Бот для сессии {session_id} уже запущен. Пропускаем.", "WARNING")
                continue

            logger.log(f"Попытка запуска бота для сессии {session_id}")
            self.start_bot(session_id, api_token)

        logger.log("Все активные боты обработаны.")

    def stop_all_bots(self):
        """
        Останавливает всех запущенных ботов.
        """
        logger.log("Остановка всех ботов...")
        if not self.active_bots:
            logger.log("Нет запущенных ботов для остановки.")
            return

        for session_id in list(self.active_bots.keys()):
            logger.log(f"Попытка остановить бота для сессии {session_id}")
            self.stop_bot(session_id)
            logger.log(f"Результат остановки бота для сессии {session_id}:")

        logger.log("Все боты остановлены.")


bot_manager = BotManager()
