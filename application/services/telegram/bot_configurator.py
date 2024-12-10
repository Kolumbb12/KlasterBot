"""
bot_configurator.py
Модуль для автоматической настройки и обновления параметров Telegram-бота через взаимодействие с BotFather.
Этот файл предоставляет функции для создания нового бота, а также обновления его имени, описания, информации о боте
(about), аватарки и фото профиля. Все обновления выполняются через команду BotFather, что позволяет изменять параметры
бота, такие как имя, описание и аватарка, используя текстовые команды и отправку файлов в чат с BotFather.
"""

import asyncio
from telethon import TelegramClient
from telethon.tl.types import InputFile
from dotenv import load_dotenv
import os
import time
import re
from utils.logs.logger import logger
from utils.utils import *


load_dotenv()

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone = os.getenv('TELEGRAM_PHONE_NUMBER')

try:
    client = TelegramClient('sessions/users_sessions/main_session/MainSession', api_id, api_hash)
except Exception as e:
    logger.log(f'Произошла ошибка во время создания клиента Telegram: {e}', 'ERROR')


async def create_bot(bot_name: str, bot_username: str) -> str:
    """
    Создает нового бота в Telegram через BotFather и возвращает его токен.

    Проверяет, что имя бота и username валидны и доступны. После этого отправляет команды
    через BotFather для создания бота с указанными параметрами.

    :param bot_name: Имя бота, которое будет отображаться пользователям.
    :param bot_username: Username бота, который должен быть уникальным и заканчиваться на 'bot'.
    :return: Возвращает токен нового бота в случае успешного создания, иначе None.
    """
    if not await check_bot_name_and_username(bot_name, bot_username):
        return f'Ошибка: Бот с username {bot_username} уже существует.'

    try:
        await client.start(phone)
    except Exception as e:
        logger.log(f'Произошла ошибка во время начала работы клиента Telegram: {e}', 'ERROR')
        return 'Произошла ошибка во время начала работы клиента Telegram'

    botfather = '@BotFather'

    try:
        await client.send_message(botfather, '/newbot')
    except Exception as e:
        logger.log(f'Произошла ошибка во время отравки команды "/newbot": {e}', 'ERROR')
        return 'Произошла ошибка во время создания бота'
    time.sleep(2)

    try:
        async for message in client.iter_messages(botfather):
            if 'Alright, a new bot' in message.text:
                await client.send_message(botfather, bot_name)
                break
    except Exception as e:
        logger.log(f'Произошла ошибка во время отравки имени бота {bot_name}: {e}', 'ERROR')
        return 'Произошла ошибка во время создания бота'
    time.sleep(2)

    try:
        async for message in client.iter_messages(botfather):
            if 'Good. Now let\'s choose a username' in message.text:
                await client.send_message(botfather, bot_username)
                break
    except Exception as e:
        logger.log(f'Произошла ошибка во время отравки юзера бота {bot_username}: {e}', 'ERROR')
        return 'Произошла ошибка во время создания бота'
    time.sleep(2)

    try:
        async for message in client.iter_messages(botfather):
            if f'Done! Congratulations on your new bot. You will find it at t.me/{bot_username}' in message.text:
                token_line = message.text
                match = re.search(r'Use this token to access the HTTP API:\s*`([^`]+)`', token_line)
                if match:
                    token = match.group(1)
                    logger.log(f'Новый бот {bot_name} | {bot_username} успешно создан')
                    return token
                else:
                    logger.log('Ошибка: Не найден токен в ответе BotFather.', 'ERROR')
                    return 'Произошла ошибка во время создания бота'
    except Exception as e:
        logger.log(f'Произошла ошибка во время получения токена бота {bot_name} | {bot_username}: {e}', 'ERROR')
        return 'Произошла ошибка во время создания бота'


def get_new_telgram_bot_token(bot_name: str, bot_username: str) -> str | None:
    """
    Получает токен для нового бота через асинхронную функцию create_bot.

    Эта функция запускает асинхронную функцию `create_bot`, которая создает нового бота в Telegram
    через BotFather и возвращает его токен.

    :param bot_name: Имя бота, которое будет отображаться пользователям.
    :param bot_username: Username бота, который должен быть уникальным и заканчиваться на 'bot'.
    :return: Токен нового бота, если создание прошло успешно, иначе None.
    """
    with client:
        return client.loop.run_until_complete(create_bot(bot_name, bot_username))


async def update_bot_name(bot_username: str, bot_name: str) -> None | str:
    """
    Обновляет имя бота.
    :param bot_username: Username бота.
    :param bot_name: Новое имя бота.
    """
    try:
        if not await is_bot_name_valid(bot_name):
            logger.log(f"Ошибка: имя бота '{about_text}' не валидно.", 'ERROR')
            return f"Ошибка: имя бота '{about_text}' не валидно."
        await client.start(phone)
        botfather = '@BotFather'
        await client.send_message(botfather, f'/setname')
        time.sleep(2)
        await client.send_message(botfather, f'@{bot_username}')
        time.sleep(2)
        await client.send_message(botfather, bot_name)
        logger.log(f"Имя бота {bot_name} успешно обновлено.", 'INFO')
        await client.disconnect()
    except Exception as e:
        logger.log(f"Ошибка при обновлении имени бота с токеном {token}: {e}", 'ERROR')


async def update_bot_about(bot_username: str, about_text: str) -> None | str:
    """
    Обновляет информацию о боте (About).
    :param bot_username: Username бота.
    :param about_text: Новый текст о боте.
    """
    try:
        if not await is_bot_about_valid(about_text):
            logger.log(f"Ошибка: Текст о боте '{about_text}' не валиден.", 'ERROR')
            return f"Ошибка: Текст о боте '{about_text}' не валиден."
        await client.start(phone)
        botfather = '@BotFather'
        await client.send_message(botfather, f'/setabouttext')
        time.sleep(2)
        await client.send_message(botfather, f'@{bot_username}')
        time.sleep(2)
        await client.send_message(botfather, about_text)
        logger.log(f"Информация о боте с username {bot_username} успешно обновлена.", 'INFO')
        await client.disconnect()
    except Exception as e:
        logger.log(f"Ошибка при обновлении информации о боте с username {bot_username}: {e}", 'ERROR')


async def update_bot_description(bot_username: str, description: str) -> None | str:
    """
    Обновляет описание бота.
    :param bot_username: Username бота.
    :param description: Новое описание бота.
    """
    try:
        if not await is_bot_description_valid(description):
            logger.log(f"Ошибка: Описание бота {about_text} не валидно.", 'ERROR')
            return f"Ошибка: Описание бота {about_text} не валидно."
        await client.start(phone)
        botfather = '@BotFather'
        await client.send_message(botfather, f'/setdescription')
        time.sleep(2)
        await client.send_message(botfather, f'@{bot_username}')
        time.sleep(2)
        await client.send_message(botfather, description)
        logger.log(f"Описание для бота {bot_username} успешно обновлено.")
        await client.disconnect()
    except Exception as e:
        logger.log(f"Ошибка при обновлении описания бота {bot_username}: {e}", "ERROR")


async def update_bot_profile_photo(bot_username: str, photo_path: str) -> None | str:
    """
    Обновляет аватарку бота.
    :param bot_username: Username бота.
    :param photo_path: Путь к файлу с аватаркой.
    """
    try:
        if not is_valid_bot_profile_photo(photo_path):
            logger.log(f"Фото для бота {bot_username} не валидно. Проверьте формат, размер и разрешение.", "ERROR")
            return f"Фото для бота {bot_username} не валидно. Проверьте формат, размер и разрешение."
        await client.start(phone)
        botfather = '@BotFather'
        await client.send_message(botfather, f'/setuserpic')
        time.sleep(2)
        await client.send_message(botfather, f'@{bot_username}')
        time.sleep(2)
        with open(photo_path, 'rb') as file:
            await client.send_file(botfather, file)
        logger.log(f"Фото бота {bot_username} успешно обновлено.")
        await client.disconnect()
    except Exception as e:
        logger.log(f"Ошибка при обновлении фото бота {bot_username}: {e}", "ERROR")


async def update_bot_description_photo(bot_username: str, photo_path: str) -> None | str:
    """
    Обновляет аватарку бота.
    :param bot_username: Username бота.
    :param photo_path: Путь к файлу с аватаркой.
    """
    try:
        if not is_valid_bot_description_photo(photo_path):
            logger.log(f"Фото для описания бота {bot_username} не валидно. Проверьте формат, размер и разрешение.", "ERROR")
            return f"Фото для описания бота {bot_username} не валидно. Проверьте формат, размер и разрешение."
        await client.start(phone)
        botfather = '@BotFather'
        await client.send_message(botfather, f'/setdescriptionpic')
        time.sleep(2)
        await client.send_message(botfather, f'@{bot_username}')
        time.sleep(2)
        with open(photo_path, 'rb') as file:
            await client.send_file(botfather, file)
        logger.log(f"Фото описания бота {bot_username} успешно обновлено.")
        await client.disconnect()
    except Exception as e:
        logger.log(f"Ошибка при обновлении фотки описания бота {bot_username}: {e}", "ERROR")


# bot_username = 'mytestmytestmytest112bot'
# token = get_new_telgram_bot_token('Test2Bot', bot_username)
# if token:
#     try:
#         client.loop.run_until_complete(update_bot_name(bot_username, "Test2_2Bot"))
#         client.loop.run_until_complete(update_bot_about(bot_username, 'Тестовое о боте'))
#         client.loop.run_until_complete(update_bot_description(bot_username, 'Это описание бота для Telegram, которое не должно превышать 512 символов.'))
#         client.loop.run_until_complete(update_bot_profile_photo(bot_username, '../../../static/images/telegram_bot_profile_images/test_2.jpg'))
#         client.loop.run_until_complete(update_bot_description_photo(bot_username, '../../../static/images/telegram_bot_profile_images/test_1.jpg'))
#     except Exception as e:
#         print(f"Ошибка: {e}")
# else:
#     print("Failed to create bot, username already taken.")