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


