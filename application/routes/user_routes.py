"""
user_routes.py
Модуль маршрутов (роутов) для управления пользователями. Содержит функции для аутентификации, управления профилем и
административного управления пользователями. Реализует маршруты для входа, выхода, изменения профиля и пароля,
добавления нового пользователя, а также для отображения списка пользователей (для администраторов).
"""

from database.db_functions import *
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from database.db_connection import db_instance


# Создаем blueprint для маршрутов, связанных с пользователями
user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/', methods=['GET'])
def index():
    """
    Маршрут главной страницы.
    Отображает анимацию сетки с кнопкой "НАЧАТЬ".
    """
    return render_template('index.html')


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Маршрут для входа пользователя в систему.

    Обрабатывает GET и POST запросы:
    - GET: Отображает страницу входа.
    - POST: Проверяет имя пользователя и пароль, устанавливает сессию при успешной аутентификации.

    :return: Шаблон login.html для GET-запросов или перенаправление при успешном входе.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = get_user_by_username(username)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['is_admin'] = bool(user['is_admin'])
            flash('Вы успешно вошли на сайт', 'success')
            return redirect(url_for('agent_bp.agent_selection'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')


@user_bp.route('/logout')
def logout():
    """
    Маршрут для выхода пользователя из системы.

    Завершает текущую сессию и перенаправляет на страницу входа.

    :return: Перенаправление на login.html.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))

    session.clear()  # Очистка сессии
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for('user_bp.login'))


@user_bp.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    """
    Маршрут для отображения и редактирования профиля пользователя.

    Обрабатывает GET и POST запросы:
    - GET: Отображает профиль пользователя.
    - POST: Обновляет профиль пользователя с новыми данными, если они предоставлены.

    :return: Шаблон user_profile.html с данными пользователя.
    """
    if 'user_id' not in session:
        flash("Пожалуйста, авторизуйтесь", "error")
        return redirect(url_for('user_bp.login'))

    user_id = request.args.get('user_id') or request.form.get('user_id') or session['user_id']
    user = select_user_by_id(user_id)

    if request.method == 'POST':
        settings = {
            'full_name': request.form.get('full_name') or None,
            'email': request.form.get('email') or None,
            'phone_number': request.form.get('phone_number') or None,
            'password': request.form.get('password') or None
        }
        try:
            update_user_profile(user_id, settings)
            flash("Профиль успешно обновлен", "success")
            return redirect(url_for('user_bp.user_profile', user_id=user_id))
        except Exception as e:
            flash(f"Ошибка: {e}", "error")

    return render_template('user_profile.html', user=user, user_id=user_id)


@user_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """
    Маршрут для изменения пароля пользователя.

    Обрабатывает GET и POST запросы:
    - GET: Отображает форму для изменения пароля.
    - POST: Обновляет пароль пользователя.

    :return: Шаблон change_password.html для GET-запросов или перенаправление на страницу профиля после изменения пароля.
    """
    if 'user_id' not in session:
        flash("Пожалуйста, авторизуйтесь", "error")
        return redirect(url_for('user_bp.login'))

    # Определяем user_id: либо из аргументов запроса, либо из сессии (для себя)
    user_id = request.args.get('user_id') or session['user_id']

    if request.method == 'POST':
        new_password = request.form.get('new_password')

        if not new_password:
            flash("Пароль не может быть пустым", "error")
            return redirect(url_for('user_bp.change_password', user_id=user_id))

        # Обновляем пароль для указанного пользователя
        update_user_password(user_id, new_password)
        flash("Пароль успешно изменен", "success")
        return redirect(url_for('user_bp.user_profile', user_id=user_id))

    return render_template('change_password.html', user_id=user_id)



@user_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Маршрут для добавления нового пользователя (доступен только администраторам).

    Обрабатывает GET и POST запросы:
    - GET: Отображает форму для добавления нового пользователя.
    - POST: Добавляет пользователя в базу данных при условии, что администратор заполнил все обязательные поля.

    :return: Шаблон add_user.html для GET-запросов или перенаправление на выбор агентов после добавления пользователя.
    """
    if 'user_id' not in session:
        flash('Пожалуйста, авторизуйтесь', 'error')
        return redirect(url_for('user_bp.login'))

    if not session.get('is_admin'):
        flash("У вас нет прав доступа", "error")
        return redirect(url_for('agent_bp.agent_selection'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form

        if username and password:
            try:
                insert_user(username=username, password=password, is_admin=int(is_admin))
                flash("Пользователь успешно добавлен", "success")
            except Exception as e:
                if "Duplicate entry" in str(e):
                    flash("Пользователь с таким именем уже существует", "error")
                else:
                    flash(f"Ошибка при добавлении пользователя: {e}", "error")
            return redirect(url_for('agent_bp.agent_selection'))
        else:
            flash("Заполните все поля", "error")

    return render_template('add_user.html')


@user_bp.route('/user_list')
def user_list():
    """
    Маршрут для отображения списка пользователей (доступен только администраторам).

    Обрабатывает GET запрос:
    - GET: Отображает список всех пользователей, доступных в системе.

    :return: Шаблон user_list.html с данными пользователей.
    """
    if not session.get('is_admin'):
        flash("У вас нет прав доступа", "error")
        return redirect(url_for('agent_bp.agent_selection'))

    users = get_all_users()  # Функция для получения всех пользователей
    return render_template('user_list.html', users=users)
