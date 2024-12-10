"""
utils.py
Модуль вспомогательных функций в приложении.
"""

from decimal import Decimal

def convert_decimals(obj):
    """
    Рекурсивно преобразует все объекты типа Decimal в структуре данных (список, словарь, или одиночный объект) в float.

    :param obj: Структура данных, которая может содержать объекты типа Decimal.
    :return: Та же структура данных, но с объектами Decimal, преобразованными в float.
    """
    if isinstance(obj, list):
        # Если объект - список, применяем функцию к каждому элементу списка
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        # Если объект - словарь, применяем функцию к каждому значению словаря
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        # Преобразуем объект Decimal в float
        return float(obj)
    else:
        # Если объект не Decimal, список или словарь, возвращаем его без изменений
        return obj


from aiogram.types import Update, Message
from aiogram.types.message import Message as AIMessage

def create_update_from_json(update_data):
    """
    Функция для создания объекта Update из данных вебхука вручную.
    """
    # Проверяем, что переданный JSON содержит ключ 'message'
    if 'message' not in update_data:
        raise ValueError("No 'message' field in update data.")
    # Получаем информацию о сообщении
    message_data = update_data['message']
    # Создаем объект Message
    message = AIMessage(**message_data)
    # Создаем объект Update
    update = Update(update_id=update_data['update_id'], message=message)
    return update


import time

# Лимит сообщений и время в секундах
USER_MESSAGE_LIMIT = 3  # Максимальное количество сообщений
TIME_LIMIT = 10  # Время, в течение которого это количество сообщений разрешено

user_message_times = {}  # Словарь для хранения временных меток сообщений пользователей

def check_spam(user_id):
    """
    Проверка, является ли сообщение спамом на основе частоты сообщений.
    """
    current_time = time.time()
    # Получаем список временных меток сообщений этого пользователя
    user_messages = user_message_times.get(user_id, [])
    # Убираем старые сообщения (которые отправлены более чем TIME_LIMIT секунд назад)
    user_messages = [timestamp for timestamp in user_messages if current_time - timestamp < TIME_LIMIT]
    # Добавляем новое сообщение
    user_messages.append(current_time)
    # Обновляем список сообщений пользователя
    user_message_times[user_id] = user_messages
    # Проверяем, не превысил ли пользователь лимит
    if len(user_messages) > USER_MESSAGE_LIMIT:
        return True  # Если сообщений слишком много, считаем, что это спам
    return False


import re
from PIL import Image
import os

async def is_username_valid(username: str) -> bool:
    """
    Проверяет, что username соответствует правилам Telegram (может содержать буквы, цифры, подчёркивания и должен заканчиваться на 'bot').
    """
    pattern = r'^[a-zA-Z0-9_]+_?bot$'
    return bool(re.match(pattern, username))


async def is_bot_name_valid(bot_name: str) -> bool:
    """
    Проверяет, что имя бота является валидным.
    Имя может содержать буквы, цифры, пробелы и подчёркивания, но не другие спецсимволы.
    """
    return bool(re.match(r'^[A-Za-z0-9 _]+$', bot_name))


async def is_username_available(username: str) -> bool:
    """
    Проверяет, доступен ли username для бота, проверяя наличие чата по ссылке t.me/{username}.
    """
    try:
        await client.get_entity(f't.me/{username}')
        return False
    except Exception:
        return True


async def check_bot_name_and_username(bot_name: str, bot_username: str) -> bool:
    """
    Проверяет, что и имя бота, и username валидны и доступны.
    """
    if not await is_bot_name_valid(bot_name):
        logger.log(f"Имя бота '{bot_name}' не валидно.", 'ERROR')
        return False
    if not await is_username_valid(bot_username):
        logger.log(f"Username '{bot_username}' не валиден. Он должен заканчиваться на 'bot' и не содержать спецсимволов.", 'ERROR')
        return False
    if not await is_username_available(bot_username):
        logger.log(f"Username '{bot_username}' уже занят.", 'ERROR')
        return False
    return True


async def is_bot_about_valid(about_text: str) -> bool:
    """
    Проверяет, что текст о боте (About) является валидным.
    Текст может содержать буквы, цифры, пробелы и спецсимволы, но не должен превышать 70 символов.
    """
    if len(about_text) > 70:
        return False
    return bool(re.match(r'^[\w _.,!?()&"\'\-а-яА-ЯёЁa-zA-Z]+$', about_text))


async def is_bot_description_valid(description: str) -> bool:
    """
    Проверяет, что текст description для бота Telegram является валидным.
    Текст может содержать буквы, цифры, пробелы и спецсимволы, но не должен превышать 512 символов.
    """
    if len(description) > 512:
        return False
    return bool(re.match(r'^[\w _.,!?()&"\'\-а-яА-ЯёЁa-zA-Z]+$', description))


def is_valid_bot_profile_photo(file_path: str) -> bool:
    """
    Проверяет, является ли фото валидным для профиля Telegram бота.

    Рекомендуемые параметры:
    - Формат: JPEG, PNG.
    - Квадратное разрешение (например, 512x512).
    - Размер файла: до 5 МБ.
    """
    if not os.path.exists(file_path):
        return False

    valid_formats = ["JPEG", "PNG"]
    max_file_size = 5 * 1024 * 1024
    try:
        if os.path.getsize(file_path) > max_file_size:
            return False
        with Image.open(file_path) as img:
            if img.format not in valid_formats:
                return False
            width, height = img.size
            if abs(width - height) / max(width, height) * 100 > 20:
                return False
        return True
    except Exception as e:
        return False


def is_valid_bot_description_photo(file_path: str) -> bool:
    """
    Проверяет валидность фото или GIF для Telegram бота.

    Требования:
    - Для фото: 640x360 пикселей.
    - Для GIF: одно из разрешений: 320x180, 640x360, 960x540 пикселей.

    Возвращает True, если файл соответствует требованиям, иначе False.
    """
    if not os.path.exists(file_path):
        return False

    valid_photo_formats = ["JPEG", "PNG"]
    valid_gif_format = "GIF"
    valid_resolutions = [
        (640, 360),
        (320, 180),
        (960, 540)
    ]

    try:
        with Image.open(file_path) as img:
            file_format = img.format
            resolution = img.size
            if file_format in valid_photo_formats and resolution == (640, 360):
                return True
            elif file_format == valid_gif_format and resolution in valid_resolutions:
                return True
            else:
                return False
    except Exception as e:
        return False
