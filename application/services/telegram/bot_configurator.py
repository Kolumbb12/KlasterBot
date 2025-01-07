"""
bot_configurator.py
Модуль для автоматической настройки и обновления параметров Telegram-бота через взаимодействие с BotFather.
Этот файл предоставляет функции для создания нового бота, а также обновления его имени, описания, информации о боте
(about), аватарки и фото профиля. Все обновления выполняются через команду BotFather, что позволяет изменять параметры
бота, такие как имя, описание и аватарка, используя текстовые команды и отправку файлов в чат с BotFather.
"""

import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
import os
import re
from utils.logs.logger import logger
from utils.utils import *
import requests


load_dotenv()

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone = os.getenv('TELEGRAM_PHONE_NUMBER')
client_path = os.getenv('TELEGRAM_CLIENT_PATH')

try:
    client = TelegramClient(client_path, api_id, api_hash)
except Exception as e:
    logger.log(f'Ошибка при создании клиента Telegram: {e}', "ERROR")
    raise


def run_async_task(coroutine):
    """
    Запуск асинхронной задачи в существующем event loop
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)


async def create_bot(bot_name: str, bot_username: str) -> str:
    """
    Создает нового бота в Telegram через BotFather и возвращает его токен.
    """
    if not await check_bot_name_and_username(bot_name, bot_username):
        return f'Ошибка: Бот с username {bot_username} уже существует.'
    await client.start(phone)
    botfather = '@BotFather'
    try:
        await client.send_message(botfather, '/newbot')
        await asyncio.sleep(2)
        await client.send_message(botfather, bot_name)
        await asyncio.sleep(2)
        await client.send_message(botfather, bot_username)
        await asyncio.sleep(2)
        async for message in client.iter_messages(botfather):
            if f'Done! Congratulations on your new bot. You will find it at t.me/{bot_username}' in message.text:
                token_line = message.text
                match = re.search(r"Use this token to access the HTTP API:\s*`([^`]+)`", token_line)
                if match:
                    token = match.group(1)
                    logger.log(f'Новый бот {bot_name} | {bot_username} успешно создан')
                    return token
                else:
                    logger.log('Ошибка: Не найден токен в ответе BotFather.', 'ERROR')
                    return 'Произошла ошибка во время создания бота'
    except Exception as e:
        logger.log(f'Ошибка при создании бота {bot_name} | {bot_username}: {e}', "ERROR")
        return 'Произошла ошибка при создании бота'
    return 'Ошибка: не удалось создать бота'


# +
def update_bot_name(token: str, bot_name: str) -> str:
    """
    Обновляет имя бота через Telegram API.

    :param token: Токен API бота.
    :param bot_name: Новое имя бота.
    :return: Статус операции.
    """
    if not is_bot_name_valid(bot_name):
        logger.log(f"Ошибка: Наименование {bot_name} не валидно.", "ERROR")
        return f"Ошибка: Наименование {bot_name} не валидно."
    url = f"https://api.telegram.org/bot{token}/setMyName"
    params = {"name": bot_name}
    try:
        response = requests.post(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("ok"):
            return "Имя бота успешно обновлено."
        else:
            return f"Ошибка: {data.get('description')}"
    except Exception as e:
        return f"Ошибка при обновлении имени бота: {e}"


# -
def update_bot_about(token: str, about_text: str) -> str:
    """
    Обновляет информацию 'О боте' через Telegram API.
    """
    if not is_bot_about_valid(about_text):
        logger.log(f"Ошибка: Текст о боте '{about_text}' не валиден.", "ERROR")
        return f"Ошибка: Текст о боте '{about_text}' не валиден."
    url = f"https://api.telegram.org/bot{token}/setMyAboutText"
    params = {"description": about_text}
    try:
        response = requests.post(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("ok"):
            return "Информация 'О боте' успешно обновлена."
        else:
            return f"Ошибка: {data.get('description')}"
    except Exception as e:
        return f"Ошибка при обновлении информации 'О боте': {e}"


# +
def update_bot_description(token: str, description: str) -> str:
    """
    Обновляет описание бота.
    """
    if not is_bot_description_valid(description):
        logger.log(f"Ошибка: Описание бота '{description}' не валидно.", "ERROR")
        return f"Ошибка: Описание бота '{description}' не валидно."
    url = f"https://api.telegram.org/bot{token}/setMyDescription"
    params = {"description": description}
    try:
        response = requests.post(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("ok"):
            return "Описание бота успешно обновлено."
        else:
            return f"Ошибка: {data.get('description')}"
    except Exception as e:
        return f"Ошибка при обновлении описания бота: {e}"


# -
def update_bot_profile_photo(token: str, photo_path: str) -> str:
    """
    Обновляет аватарку бота.
    """
    if not is_valid_bot_profile_photo(photo_path):
        logger.log("Фото профиля бота не валидно. Проверьте формат, размер и разрешение.", "ERROR")
        return "Фото профиля бота не валидно. Проверьте формат, размер и разрешение."
    url = f"https://api.telegram.org/bot{token}/SetMyProfilePhoto"
    with open(photo_path, "rb") as photo_file:
        files = {"photo": photo_file}
        try:
            response = requests.post(url, files=files, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("ok"):
                return "Фото профиля успешно обновлено."
            else:
                return f"Ошибка: {data.get('description')}"
        except Exception as e:
            return f"Ошибка при обновлении фото профиля: {e}"


# -
def update_bot_description_photo(token: str, photo_path: str) -> str:
    """
    Обновляет аватарку бота.
    """
    if not is_valid_bot_description_photo(photo_path):
        logger.log("Фото описания бота не валидно. Проверьте формат, размер и разрешение.", "ERROR")
        return "Фото описания бота не валидно. Проверьте формат, размер и разрешение."
    url = f"https://api.telegram.org/bot{token}/setMyDescriptionPhoto"
    with open(photo_path, "rb") as photo_file:
        files = {"photo": photo_file}
        try:
            response = requests.post(url, files=files, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("ok"):
                return "Фото описания успешно обновлено."
            else:
                return f"Ошибка: {data.get('description')}"
        except Exception as e:
            return f"Ошибка при обновлении фото профиля: {e}"
