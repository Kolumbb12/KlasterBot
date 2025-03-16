"""
utils.py
Модуль вспомогательных функций в приложении.
"""

import re

def validate_full_name(full_name):
    """
    Проверяет корректность полного имени.
    :param full_name: Строка с полным именем.
    :return: Сообщение об ошибке или None, если имя корректное.
    """
    if full_name and len(full_name) > 100:
        return "Полное имя не может превышать 100 символов."
    return None

import re

def validate_email(email):
    """
    Проверяет корректность email.
    :param email: Строка с email.
    :return: Сообщение об ошибке или None, если email корректный.
    """
    if email:
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return "Некорректный формат email."
        if len(email) > 100:
            return "Email не может превышать 100 символов."
    return None

def validate_phone_number(phone_number):
    """
    Проверяет корректность номера телефона с использованием регулярных выражений.
    :param phone_number: Строка с номером телефона.
    :return: Сообщение об ошибке или None, если номер корректный.
    """
    if not phone_number:
        return "Номер телефона не может быть пустым."
    # Регулярное выражение для проверки номера телефона
    pattern = re.compile(r'^\+?[0-9\s\-\(\)]{6,15}$')
    if not pattern.match(phone_number):
        return "Номер телефона имеет неверный формат."
    # Удаляем все нецифровые символы для проверки длины
    digits_only = re.sub(r'[^0-9]', '', phone_number)
    if len(digits_only) < 6 or len(digits_only) > 15:
        return "Номер телефона должен содержать от 6 до 15 цифр."
    return None

def validate_password(password):
    """
    Проверяет корректность пароля.
    :param password: Строка с паролем.
    :return: Сообщение об ошибке или None, если пароль корректный.
    """
    if password and len(password) < 8:
        return "Пароль должен содержать не менее 8 символов."
    return None


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


import requests

def is_valid_telegram_token(token: str) -> bool:
    """
    Проверяет валидность API-токена Telegram.

    :param token: API-токен Telegram бота
    :return: True, если токен валиден, иначе False
    """
    if not token or ":" not in token:  # Проверка базового формата токена
        return False

    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=5)  # Запрос к Telegram API
        response.raise_for_status()  # Генерирует исключение для HTTP ошибок
        data = response.json()  # Расшифровка ответа JSON

        # Проверка на корректный ответ от Telegram
        if data.get("ok") and "result" in data:
            return True
        return False
    except requests.HTTPError as e:
        print(f"HTTP ошибка при проверке токена: {e}")
        return False
    except requests.RequestException as e:
        print(f"Ошибка соединения при проверке токена: {e}")
        return False
    except ValueError as e:
        print(f"Ошибка при разборе ответа JSON: {e}")
        return False


import re
from PIL import Image
import os

def is_username_valid(username: str) -> bool:
    """
    Проверяет, что username соответствует правилам Telegram (может содержать буквы, цифры, подчёркивания и должен заканчиваться на 'bot').
    """
    pattern = r'^[a-zA-Z0-9_]+_?bot$'
    return bool(re.match(pattern, username))


def is_bot_name_valid(bot_name: str) -> bool:
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
    if not is_bot_name_valid(bot_name):
        logger.log(f"Имя бота '{bot_name}' не валидно.", 'ERROR')
        return False
    if not is_username_valid(bot_username):
        logger.log(f"Username '{bot_username}' не валиден. Он должен заканчиваться на 'bot' и не содержать спецсимволов.", 'ERROR')
        return False
    if not await is_username_available(bot_username):
        logger.log(f"Username '{bot_username}' уже занят.", 'ERROR')
        return False
    return True


def is_bot_about_valid(about_text: str) -> bool:
    """
    Проверяет, что текст о боте (About) является валидным.
    Текст может содержать буквы, цифры, пробелы и спецсимволы, но не должен превышать 70 символов.
    """
    if len(about_text) > 70:
        return False
    return bool(re.match(r'^[\w _.,!?()&"\'\-а-яА-ЯёЁa-zA-Z]+$', about_text))


def is_bot_description_valid(description: str) -> bool:
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
    except Exception:
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
    except Exception:
        return False


import requests

def get_telegram_bot_name_and_username_by_token(api_token: str):
    """
    Получает имя и username Telegram-бота по его токену.

    :param api_token: Токен бота.
    :return: Кортеж (first_name, username), если токен валиден.
             None, если токен недействителен или произошла ошибка.
    """
    url = f"https://api.telegram.org/bot{api_token}/getMe"
    try:
        response = requests.get(url, timeout=5)  # Запрос к Telegram API
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                first_name = bot_info.get("first_name")
                username = bot_info.get("username")
                return first_name, username
        return None
    except requests.RequestException:
        return None
