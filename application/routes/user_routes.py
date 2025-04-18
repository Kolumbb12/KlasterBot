"""
user_routes.py
Модуль маршрутов (роутов) для управления пользователями. Содержит функции для аутентификации, управления профилем и
административного управления пользователями. Реализует маршруты для входа, выхода, изменения профиля и пароля,
добавления нового пользователя, а также для отображения списка пользователей (для администраторов).
"""

from database.db_functions import *
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from database.db_connection import db_instance
from utils.access_control import has_access, limiter, custom_limit_key
from utils.utils import validate_full_name, validate_email, validate_phone_number, validate_password


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
            session['role_id'] = user['role_id']
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


@user_bp.route('/user_list')
@limiter.limit("5 per minute", key_func=custom_limit_key)
def user_list():
    """
    Маршрут для отображения списка пользователей (доступен только администраторам).

    Обрабатывает GET запрос:
    - GET: Отображает список всех пользователей, доступных в системе.

    :return: Шаблон user_list.html с данными пользователей.
    """
    if session.get('role_id') != 1:
        flash("У вас нет прав доступа", "error")
        return redirect(url_for('agent_bp.agent_selection'))
    users = get_all_users()  # Функция для получения всех пользователей
    print(users)
    return render_template('user_list.html', users=users)


@user_bp.route('/user_profile', methods=['GET', 'POST'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
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

    user_id = request.args.get('user_id') or session.get('user_id')

    print(user_id)

    if session.get('role_id') != 1:
        if not has_access(user_id, 'user', session['user_id'], session.get('role_id')):
            flash("У вас нет прав на доступ к этому профилю.", "error")
            return redirect(url_for('user_bp.user_profile'))

    user = get_user_by_id(user_id)

    if request.method == 'POST':

        settings = {
            'full_name': request.form.get('full_name') or None,
            'email': request.form.get('email') or None,
            'phone_number': request.form.get('phone_number') or None,
            'password': request.form.get('password') or No
        }

        errors = []

        # Проверка полей
        full_name_error = validate_full_name(settings['full_name'])
        if full_name_error:
            errors.append(full_name_error)

        email_error = validate_email(settings['email'])
        if email_error:
            errors.append(email_error)

        phone_error = validate_phone_number(settings['phone_number'])
        if phone_error:
            errors.append(phone_error)

        password_error = validate_password(settings['password'])
        if password_error:
            errors.append(password_error)

        # Если есть ошибки, возвращаем их пользователю
        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for('user_bp.user_profile', user_id=user_id))

        try:
            update_user_profile(user_id, settings)
            flash("Профиль успешно обновлен", "success")
            return redirect(url_for('user_bp.user_profile', user_id=user_id))
        except Exception as e:
            flash(f"Ошибка: {e}", "error")

    return render_template('user_profile.html', user=user, user_id=user_id)


@user_bp.route('/change_password', methods=['GET', 'POST'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
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

    if not has_access(user_id, 'user', session['user_id'], session.get('role_id')):
        flash("У вас нет прав на доступ к этому профилю.", "error")
        return redirect(url_for('session_bp.sessions'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')

        if not new_password:
            flash("Пароль не может быть пустым", "error")
            return redirect(url_for('user_bp.change_password', user_id=user_id))

        password_error = validate_password(new_password)
        if password_error:
            flash(password_error, "error")
            return redirect(url_for('user_bp.user_profile', user_id=user_id))

        # Обновляем пароль для указанного пользователя
        update_user_password(user_id, new_password)
        flash("Пароль успешно изменен", "success")
        return redirect(url_for('user_bp.user_profile', user_id=user_id))

    return render_template('change_password.html', user_id=user_id)



@user_bp.route('/add_user', methods=['GET', 'POST'])
@limiter.limit("5 per minute", key_func=custom_limit_key)
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

    if session.get('role_id') != 1:
        flash("У вас нет прав доступа", "error")
        return redirect(url_for('agent_bp.agent_selection'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_id = int('role_id' in request.form)
        role_id = role_id + 2 if role_id == 0 else role_id

        if username and password:
            try:
                new_id = get_last_user_id()
                insert_user(id=new_id, username=username, password=password, role_id=role_id)
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
