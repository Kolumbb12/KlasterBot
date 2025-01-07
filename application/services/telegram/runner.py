"""
runner.py
Модуль для запуска и управления Telegram-ботами с использованием библиотеки Aiogram.

Этот файл содержит класс `BotRunner`, который позволяет запускать бота на вебхуке с использованием aiohttp-сервера.
Он включает методы для обработки команд и сообщений, а также для остановки бота.

Основные функции:
1. **start_webhook**:
   - Настроить и запустить сервер с использованием aiohttp для обработки запросов Telegram.
   - Обработать команду `/start`, отправляя приветственное сообщение.
   - Обрабатывать все входящие сообщения, генерируя ответ с использованием GPT API и записывая историю чата в базу данных.
2. **stop_webhook**:
   - Остановить работу бота, удалив вебхук и завершив сессию.

Для каждого бота создается уникальный сервер с портом, основанным на идентификаторе сессии.
"""

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from database.db_functions import *
from utils.web_clients.gpt_api import generate_response
from utils.logs.logger import logger
from utils.utils import check_spam
from dotenv import load_dotenv
import os


load_dotenv()


class BotRunner:

    def __init__(self, session_id, token, port):
        self.session_id = session_id
        self.token = token
        self.port = port  # Порт, который будет использовать бот
        self.bot = Bot(token=self.token, skip_updates=False)  # Инициализация бота
        self.dp = Dispatcher()  # Инициализация диспетчера
        self.dp["bot"] = self.bot  # Добавление бота в контекст диспетчера
        self.webhook_url = f"{os.getenv('NGROK_ADDRESS')}/webhook/{self.session_id}"

    async def start_webhook(self):
        """
        Настройка Webhook и запуск aiohttp-сервера для получения обновлений от Telegram.
        """
        # Регистрация обработчика команды /start
        @self.dp.message(Command(commands=["start"]))
        async def start_handler(message: Message):
            user_id = message.from_user.id
            if check_spam(user_id):
                await message.answer("Вы слишком часто отправляете сообщения. Пожалуйста, подождите.")
                return
            if not check_user_exists(user_id):
                username = message.from_user.username or ''
                first_name = message.from_user.first_name or ''
                last_name = message.from_user.last_name or ''
                insert_user(user_id, username, '', 3, f'{last_name} {first_name}')
            session = get_session_by_id(self.session_id)
            agent = select_agent_by_id(session['agent_id'])
            start_message = agent.get("start_message", "Добро пожаловать!")
            await message.answer(start_message)

        # Регистрация обработчика любых сообщений
        @self.dp.message()
        async def echo_handler(message: Message):
            user_id = message.from_user.id
            if check_spam(user_id):
                await message.answer("Вы слишком часто отправляете сообщения. Пожалуйста, подождите.")
                return
            if not check_user_exists(user_id):
                username = message.from_user.username or ''
                first_name = message.from_user.first_name or ''
                last_name = message.from_user.last_name or ''
                insert_user(user_id, username, '', 3, f'{last_name} {first_name}')
            session = get_session_by_id(self.session_id)
            user_input = message.text
            agent = select_agent_by_id(session['agent_id'])
            conversation_history = get_chat_history_by_session_id_and_user_id(self.session_id, user_id) or []
            response = generate_response(agent_id=agent['id'], user_input=user_input, conversation_history=conversation_history)
            await message.answer(response)
            insert_chat_message_for_session(user_id, agent['id'], 2, self.session_id, user_input, response)

        # Настройка Webhook в Telegram
        await self.bot.set_webhook(self.webhook_url, drop_pending_updates=True)

        # Настройка aiohttp-приложения для обработки Webhook
        app = web.Application()
        SimpleRequestHandler(dispatcher=self.dp, bot=self.bot).register(app, path="")
        setup_application(app, self.dp)

        # Запуск aiohttp-сервера на уникальном порту
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", self.port)  # Используем уникальный порт
        await site.start()

    async def stop_webhook(self):
        """
        Удаление Webhook и остановка aiohttp-приложения.
        """
        await self.bot.delete_webhook()
        await self.dp.shutdown()
        await self.bot.session.close()
