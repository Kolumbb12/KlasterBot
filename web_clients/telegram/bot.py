"""
bot.py
Этот файл предназначен для интеграции с API Telegram. В этом модуле будут реализованы функции для взаимодействия с
Telegram, включая отправку и получение сообщений, обработку команд и управление ботом.
Функции модуля будут использоваться для интеграции проекта с платформой Telegram и обеспечения общения через нее.

Планируемые функции:
1. Отправка сообщений пользователям Telegram.
2. Обработка входящих сообщений и команд.
3. Интеграция с основным приложением для передачи данных между пользователем и ботом через Telegram.
"""

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor


def start_bot(api_token):
    bot = Bot(token=api_token)
    dp = Dispatcher(bot)

    @dp.message_handler(commands=['start'])
    async def send_welcome(message: types.Message):
        await message.reply("Привет! Я ваш помощник.")

    executor.start_polling(dp, skip_updates=True)


@dp.message_handler()
async def handle_message(message: types.Message):
    # Определение бота, от которого пришло сообщение
    bot_token = bot.token
    session_id = get_session_id_by_token(bot_token)  # Ваш метод поиска сессии
    agent_id = get_agent_id_by_session(session_id)  # Связь с агентом

    # Логика обработки
    response = get_agent_response(agent_id, message.text)
    await message.reply(response)