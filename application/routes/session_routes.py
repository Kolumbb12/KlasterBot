"""
session_routes.py
Модуль маршрутов (роутов) для управления сессиями. Содержит функции для:
- Отображения списка активных сессий.
- Назначения платформы для агента.
- Создания новой сессии.
- Завершения активной сессии.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from database.db_functions import *

# Создаём Blueprint для маршрутов, связанных с управлением сессиями
session_bp = Blueprint('session_bp', __name__)


# Маршрут для отображения страницы выбора платформы для агента
@session_bp.route('/sessions/assign/<int:agent_id>', methods=['GET'])
def assign_platform(agent_id):
    """
    Отображение страницы для назначения платформы агенту.

    - Принимает ID агента в качестве параметра.
    - Извлекает информацию об агенте и доступные платформы.
    - Возвращает шаблон `assign_platform.html` с данными агента и платформ.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    try:
        agent = select_agent_by_id(agent_id)  # Получение информации об агенте
        platforms = get_available_platforms(agent_id)  # Получение списка доступных платформ
        return render_template('assign_platform.html', agent=agent, platforms=platforms)
    except Exception as e:
        flash(f"Ошибка при загрузке страницы назначения платформы: {e}", "error")
        return redirect(url_for('session_bp.sessions'))


@session_bp.route('/sessions/create/<int:agent_id>', methods=['POST'])
def create_session(agent_id):
    """
    Создание новой сессии для агента и перенаправление на соответствующий шаблон.

    - Получает ID агента и выбранную платформу.
    - Создаёт запись сессии в базе данных.
    - Перенаправляет на уникальный шаблон в зависимости от платформы.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    try:
        user_id = session['user_id']
        platform_id = int(request.form.get('platform'))  # Получение chat_type_id из формы

        # Логика создания новой сессии
        session_id = add_session(user_id, agent_id, platform_id)  # Возвращает ID созданной сессии

        # Определяем шаблон в зависимости от платформы
        if platform_id == 2:  # Telegram (Бот)
            return redirect(url_for('session_bp.telegram_bot_setup', session_id=session_id))
        elif platform_id == 3:  # Telegram (Пользователь)
            return redirect(url_for('session_bp.telegram_user_setup', session_id=session_id))
        if platform_id == 4:  # WhatsApp (Бот)
            return redirect(url_for('session_bp.whatsapp_bot_setup', session_id=session_id))
        elif platform_id == 5:  # WhatsApp (Пользователь)
            return redirect(url_for('session_bp.whatsapp_user_setup', session_id=session_id))
        else:
            flash("Выбрана неподдерживаемая платформа.", "error")
            return redirect(url_for('session_bp.sessions'))

    except Exception as e:
        flash(f"Ошибка при создании сессии: {e}", "error")
        return redirect(url_for('session_bp.sessions'))

# Маршрут для отображения списка активных сессий пользователя
@session_bp.route('/sessions')
def sessions():
    """
    Отображение всех активных сессий текущего пользователя.

    - Извлекает ID текущего пользователя из сессии.
    - Получает список сессий пользователя с использованием функции `get_user_sessions`.
    - Возвращает шаблон `sessions.html`, где отображается список сессий.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    user_id = session.get('user_id')  # Получение ID текущего пользователя
    user_sessions = get_user_sessions(user_id)  # Получение списка сессий пользователя
    return render_template('sessions.html', user_sessions=user_sessions)


@session_bp.route('/sessions/session/<int:session_id>', method=['GET', 'POST'])
def session(session_id):
    """

    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))
    pass
    pass
    pass


# Маршрут для активации сессии
@session_bp.route('/sessions/activate/<int:session_id>', methods=['GET'])
def activate_session(session_id):
    """
    Завершение активной сессии.

    - Принимает ID сессии в качестве параметра.
    - Вызывает функцию `terminate_session` для завершения сессии в базе данных.
    - Перенаправляет на страницу списка сессий с уведомлением.
    """
    # activate_session(session_id)  # Активация сессии в базе данных
    # flash('Сессия успешно завершена.', 'info')  # Сообщение об успешном завершении
    # return redirect(url_for('session_bp.sessions'))
    start_bot()


# Маршрут для завершения активной сессии
@session_bp.route('/sessions/terminate/<int:session_id>', methods=['GET'])
def terminate_session(session_id):
    """
    Завершение активной сессии.

    - Принимает ID сессии в качестве параметра.
    - Вызывает функцию `terminate_session` для завершения сессии в базе данных.
    - Перенаправляет на страницу списка сессий с уведомлением.
    """
    # terminate_session(session_id)  # Завершение сессии в базе данных
    # flash('Сессия успешно завершена.', 'info')  # Сообщение об успешном завершении
    # return redirect(url_for('session_bp.sessions'))


############################################### Роуты для работы telegram ##############################################


