"""
access_control.py
Модуль для управления доступом к различным ресурсам приложения. Содержит универсальную функцию `has_access`,
которая проверяет, имеет ли пользователь право доступа к указанному ресурсу.
"""

from database.db_functions import (
    get_agent_by_id,
    get_session_by_id,
    get_user_by_id
)

def has_access(resource_id, resource_type, user_id, role_id):
    """
    Универсальная функция для проверки прав доступа к ресурсам.
    :param resource_id: ID ресурса.
    :param resource_type: Тип ресурса (например, 'agent', 'session', 'user').
    :param user_id: ID текущего пользователя, запрашивающего доступ.
    :param role_id: Роль текущего пользователя (1 — администратор).
    :return: True, если доступ разрешен, иначе False.
    """
    # Сопоставление типов ресурсов с соответствующими функциями получения данных
    resource_map = {
        'agent': get_agent_by_id,
        'session': get_session_by_id,
        'user': get_user_by_id,
    }

    # Проверка на допустимый тип ресурса
    if resource_type not in resource_map:
        raise ValueError("Неверный тип ресурса")

    # Получение данных ресурса
    resource = resource_map[resource_type](resource_id)
    if not resource:
        return False  # Ресурс не найден

    # Проверка прав доступа: либо владелец ресурса, либо администратор
    return resource['user_id'] == user_id or role_id == 1


from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=lambda: f"{get_remote_address()}-{session.get('user_id', 'anonymous')}",
    default_limits=["10 per minute"]
)

from flask import session
from flask_limiter.util import get_remote_address

def custom_limit_key():
    """
    Генерация ключа для лимитера.
    Используется комбинация IP-адреса и user_id из сессии.
    Если user_id отсутствует, используется только IP.
    """
    user_id = session.get('user_id', 'anonymous')
    return f"{get_remote_address()}-{user_id}"