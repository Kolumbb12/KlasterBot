"""
db_functions.py
Файл, содержащий функции для работы с таблицами базы данных: users, gpt_agents и chats.
Этот файл предоставляет доступ к данным и позволяет выполнять CRUD операции (создание, чтение, обновление, удаление)
для таблиц, таких как users (пользователи), gpt_agents (агенты GPT) и chats (история чатов).
"""

from mysql.connector import Error
from database.db_connection import db_instance
from utils.logs.logger import logger
from application.services.telegram.bot_configurator import update_bot_name, update_bot_description

######################################## Функции для работы с таблицей "users" #########################################

def select_user_by_id(user_id):
    """
    Извлекает данные пользователя по его ID.
    :param user_id: ID пользователя, данные которого нужно получить.
    :return: Словарь с данными пользователя (username, пароль, имя и т.д.), если пользователь существует.
    Возвращает None, если пользователь не найден.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s AND is_deleted = FALSE", (user_id,))
            user = cursor.fetchone()
            return user
    except Error as e:
        logger.log(f"Ошибка при получении пользователя: {e}", "ERROR")


def get_user_by_username(username):
    """
    Извлекает данные пользователя по его имени пользователя.
    :param username: Имя пользователя, данные которого нужно получить.
    :return: Словарь с данными пользователя (username, пароль, имя и т.д.), если пользователь существует.
    Возвращает None, если пользователь не найден.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s AND is_deleted = FALSE", (username,))
            user = cursor.fetchone()
            return user
    except Error as e:
        logger.log(f"Ошибка при получении пользователя: {e}", "ERROR")


def get_all_users():
    """
    Извлекает список всех активных пользователей (которые не были помечены как удаленные).
    :return: Список словарей с данными пользователей (id и username) для каждого активного пользователя.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, username, full_name FROM users WHERE is_deleted = 0")
            users = cursor.fetchall()
            return users
    except Error as e:
        logger.log(f"Ошибка при получении списка пользователей: {e}", "ERROR")


def insert_user(id, username, password, role_id, full_name=''):
    """
    Вставляет нового пользователя в базу данных с указанными именем пользователя, паролем и статусом администратора.
    :param id: id пользователя.
    :param username: Имя нового пользователя (уникальное).
    :param password: Пароль нового пользователя.
    :param role_id: id роли.
    :param full_name: Полное имя пользователя (если есть).
    :raises ValueError: Если имя пользователя уже занято, вызывает исключение с сообщением об ошибке.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
            "INSERT INTO users (id, username, password, role_id, full_name) VALUES (%s, %s, %s, %s, %s)",
            (id, username, password, role_id, full_name)
        )
        connection.commit()
    except Error as e:
        if "Duplicate entry" in str(e):
            raise ValueError("Пользователь с таким именем уже существует.")
        else:
            raise e


def update_user_password(user_id, new_password):
    """
    Обновляет пароль пользователя по его ID.
    :param user_id: ID пользователя, пароль которого нужно обновить.
    :param new_password: Новый пароль пользователя.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password = %s WHERE id = %s AND is_deleted = FALSE",
                (new_password, user_id)
            )
            connection.commit()
    except Error as e:
        logger.log(f"Ошибка при обновлении пароля: {e}", "ERROR")


def update_user_profile(user_id, settings):
    """
    Обновляет профиль пользователя. Доступные для обновления поля включают полное имя, email, телефон и пароль.
    :param user_id: ID пользователя, профиль которого нужно обновить.
    :param settings: Словарь с ключами и значениями для обновления (например, {'full_name': 'Иванов Иван Иванович'}).
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            # Формирование динамического SQL-запроса для обновления
            update_fields = []
            values = []
            for field, value in settings.items():
                if field in ('full_name', 'email', 'phone_number', 'password') and value is not None:
                    update_fields.append(f"{field} = %s")
                    values.append(value)
            if update_fields:
                update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s AND is_deleted = FALSE"
                values.append(user_id)
                cursor.execute(update_query, values)
                connection.commit()
            else:
                logger.log("Нет допустимых полей для обновления.", "ERROR")
    except Error as e:
        logger.log(f"Ошибка при обновлении профиля пользователя: {e}", "ERROR")


def get_last_user_id():
    """
    Возвращает последний id пользователя в диапазоне до 10000.
    :return: Последний id в диапазоне до 10000 или None, если таких пользователей нет.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(id) + 1 FROM users WHERE id <= 10000")
            result = cursor.fetchone()
            return result[0]
    except Error as e:
        logger.log(f"Ошибка при получении последнего id пользователя: {e}", "ERROR")
        return None


def check_user_exists(user_id):
    """
    Проверяет, существует ли пользователь с указанным ID.
    :param user_id: ID пользователя, которого нужно проверить.
    :return: True, если пользователь существует, иначе False.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] > 0
    except Error as e:
        logger.log(f"Ошибка при проверке пользователя: {e}", "ERROR")
        return False


def get_users_by_session_id(session_id):
    """
    Получает список пользователей с историей чатов для указанной сессии.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            query = """
                SELECT DISTINCT u.id, u.full_name, u.username
                FROM chats c
                INNER JOIN users u ON c.user_id = u.id
                WHERE c.session_id = %s AND c.is_deleted = FALSE
            """
            cursor.execute(query, (session_id,))
            users = cursor.fetchall()
            return users
    except Error as e:
        logger.log(f"Ошибка при получении пользователей для сессии: {e}", "ERROR")
        return []


###################################### Функции для работы с таблицей "gpt_agents" ######################################

def select_agent_by_id(agent_id):
    """
    Извлекает данные агента GPT по его ID.
    :param agent_id: ID агента GPT, данные которого нужно получить.
    :return: Словарь с данными агента (имя, инструкция и т.д.), если агент существует. Возвращает None,
    если агент не найден.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM gpt_agents WHERE id = %s AND is_deleted = FALSE", (agent_id,))
            agent = cursor.fetchone()
            return agent
    except Error as e:
        logger.log(f"Ошибка при получении агента: {e}", "ERROR")


def insert_agent(user_id, name, instruction, start_message, error_message, temperature=0.5, max_tokens=150,
                 message_buffer=0, accumulate_messages=False, transmit_date=False, api_key=None):
    """
    Добавляет нового агента GPT в базу данных.
    :param user_id: ID пользователя, которому принадлежит агент.
    :param name: Имя агента.
    :param instruction: Инструкция для агента.
    :param start_message: Приветственное сообщение.
    :param error_message: Сообщение об ошибке.
    :param temperature: Температура для генерации текста.
    :param max_tokens: Максимальное количество токенов для ответа.
    :param message_buffer: Буфер сообщений.
    :param accumulate_messages: Флаг накопления сообщений.
    :param transmit_date: Флаг передачи даты.
    :param api_key: API ключ для агента.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO gpt_agents (user_id, name, instruction, start_message, error_message, temperature, max_tokens, message_buffer, accumulate_messages, transmit_date, api_key) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (user_id, name, instruction, start_message, error_message, temperature, max_tokens, message_buffer,
                 accumulate_messages, transmit_date, api_key)
            )
            connection.commit()
    except Error as e:
        logger.log(f"Ошибка при добавлении агента: {e}", "ERROR")


def select_all_agents_by_user_id(user_id):
    """
    Извлекает всех агентов, связанных с конкретным пользователем, из базы данных.
    :param user_id: ID пользователя, для которого нужно получить агентов.
    :return: Список агентов, принадлежащих пользователю, в формате словаря.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM gpt_agents WHERE user_id = %s AND is_deleted = FALSE", (user_id,))
            agents = cursor.fetchall()
            return agents
    except Error as e:
        logger.log(f"Ошибка при получении агентов пользователя: {e}", "ERROR")


def select_all_agents_except_user(user_id):
    """
    Извлекает всех агентов, кроме агентов указанного пользователя, из базы данных.
    :param user_id: ID пользователя, чьи агенты нужно исключить.
    :return: Список агентов, не принадлежащих указанному пользователю.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT a.id, a.name, a.is_active, 
                       CASE WHEN u.full_name IS NOT NULL THEN u.full_name ELSE u.username END AS user_name
                FROM gpt_agents a
                INNER JOIN users u ON a.user_id = u.id
                WHERE a.user_id != %s AND a.is_deleted = FALSE
            """, (user_id,))
            agents = cursor.fetchall()
            return agents
    except Error as e:
        logger.log(f"Ошибка при получении агентов: {e}", "ERROR")
        return []


def update_agent_settings(agent_id, settings):
    """
    Обновляет настройки агента в базе данных для указанного агентского ID.
    :param agent_id: ID агента, для которого нужно обновить настройки.
    :param settings: Словарь с полями и их новыми значениями для обновления.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            # Формируем динамический запрос SQL для обновления только указанных полей
            update_fields = []
            values = []
            for field, value in settings.items():
                if field not in ('created_at', 'is_active'):  # Исключаем неизменяемые поля
                    update_fields.append(f"{field} = %s")
                    values.append(value)
            # Выполняем обновление, если есть поля для обновления
            if update_fields:
                update_query = f"UPDATE gpt_agents SET {', '.join(update_fields)} WHERE id = %s AND is_deleted = FALSE"
                values.append(agent_id)
                cursor.execute(update_query, values)
                connection.commit()
                logger.log("Настройки агента обновлены.", "ERROR")
            else:
                logger.log("Нет допустимых полей для обновления.", "ERROR")
    except Error as e:
        logger.log(f"Ошибка при обновлении настроек агента: {e}", "ERROR")


def set_agent_active_status(agent_id, is_active):
    """
    Изменяет статус активности агента.
    :param agent_id: ID агента, для которого нужно изменить статус.
    :param is_active: Новое значение статуса активности (True или False).
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE gpt_agents SET is_active = %s WHERE id = %s AND is_deleted = FALSE",
                (is_active, agent_id)
            )
            connection.commit()
    except Error as e:
        logger.log(f"Ошибка при изменении статуса агента: {e}", "ERROR")


######################################### Функции для работы таблицей с "chats" ########################################

def get_chat_history_by_user_and_agent(user_id, agent_id, chat_type_id):
    """
    Извлекает историю чата для заданного пользователя, агента и типа чата.
    :param user_id: ID пользователя, чья история чата требуется.
    :param agent_id: ID агента, связанного с этим чатом.
    :param chat_type_id: ID типа чата (например, 1 - тестовый чат).
    :return: Список словарей с сообщениями чата, где каждое сообщение включает роль (user или assistant) и текст сообщения (content). Если история пуста, возвращается пустой список.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            query = """
            SELECT user_message, bot_response 
            FROM chats
            WHERE user_id = %s AND agent_id = %s AND chat_type_id = %s AND is_deleted = FALSE
            ORDER BY created_at
            """
            cursor.execute(query, (user_id, agent_id, chat_type_id))
            history = cursor.fetchall()
            # Формируем список словарей для передачи истории чата в шаблон
            conversation_history = []
            for record in history:
                if record['user_message']:
                    conversation_history.append({"role": "user", "content": record['user_message']})
                if record['bot_response']:
                    conversation_history.append({"role": "assistant", "content": record['bot_response']})
            return conversation_history
    except Error as e:
        logger.log(f"Ошибка при чтении истории чата: {e}", "ERROR")


def get_chat_history_by_session_id_and_user_id(session_id, user_id):
    """
    Извлекает историю чата для заданной сессии и пользователя с дополнительными данными.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            query = """
            SELECT 
                c.id AS chat_id, 
                c.user_message, 
                c.bot_response, 
                u.full_name AS user_name, 
                tb.bot_name
            FROM chats c
            INNER JOIN users u ON c.user_id = u.id
            INNER JOIN sessions s ON c.session_id = s.id
            INNER JOIN telegram_bots tb ON c.session_id = tb.session_id
            WHERE c.session_id = %s 
              AND c.user_id = %s 
              AND c.is_deleted = FALSE
            ORDER BY c.created_at ASC
            """
            cursor.execute(query, (session_id, user_id))
            history = cursor.fetchall()
            # Формируем список сообщений
            conversation_history = []
            for record in history:
                if record['user_message']:
                    conversation_history.append({"role": "user", "content": record['user_message'],
                                                 "user_name": record['user_name'], "bot_name": record['bot_name']})
                if record['bot_response']:
                    conversation_history.append({"role": "assistant", "content": record['bot_response'],
                                                 "user_name": record['user_name'], "bot_name": record['bot_name']})
            return conversation_history
    except Error as e:
        logger.log(f"Ошибка при чтении истории чата: {e}", "ERROR")
        return []


def insert_chat_message(user_id, agent_id, chat_type_id, user_message, bot_response):
    """
    Вставляет новое сообщение чата в базу данных.

    :param user_id: ID пользователя, отправившего сообщение.
    :param agent_id: ID агента, участвующего в чате.
    :param chat_type_id: ID типа чата.
    :param user_message: Текст сообщения пользователя.
    :param bot_response: Текст ответа бота.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            query = """
            INSERT INTO chats (user_id, agent_id, chat_type_id, user_message, bot_response)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, agent_id, chat_type_id, user_message, bot_response))
            connection.commit()
    except Error as e:
        logger.log(f"Ошибка при записи истории чата: {e}", "ERROR")



def insert_chat_message_for_session(user_id, agent_id, chat_type_id, session_id, user_message, bot_response):
    """
    Вставляет новое сообщение чата для Telegram с учетом session_id.
    :param session_id: ID сессии, для которой вставляется сообщение.
    :param user_id: ID пользователя, отправившего сообщение.
    :param agent_id: ID агента, участвующего в чате.
    :param chat_type_id: ID типа чата.
    :param user_message: Текст сообщения пользователя.
    :param bot_response: Текст ответа бота.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            query = """
            INSERT INTO chats (user_id, agent_id, chat_type_id, session_id, user_message, bot_response)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, agent_id, chat_type_id, session_id, user_message, bot_response))
            connection.commit()
    except Error as e:
        logger.log(f"Ошибка при записи истории чата: {e}", "ERROR")


def delete_chat_history(user_id, agent_id, chat_type_id):
    """
    Помечает все сообщения чата как удаленные (soft delete) для заданного пользователя, агента и типа чата.
    :param user_id: ID пользователя, для которого необходимо очистить историю чата.
    :param agent_id: ID агента, связанного с этим чатом.
    :param chat_type_id: ID типа чата.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE chats 
                SET is_deleted = TRUE 
                WHERE user_id = %s AND agent_id = %s AND chat_type_id = %s
            """, (user_id, agent_id, chat_type_id))
            connection.commit()
        logger.log("История чата успешно удалена.", "ERROR")
    except Error as e:
        logger.log(f"Ошибка при удалении истории чата: {e}", "ERROR")


####################################### Функции для работы с таблицей "sessions" #######################################

def get_available_platforms(agent_id):
    """
    Извлекает список доступных платформ для агента, исключая те, для которых сессии уже созданы.
    :param agent_id: ID агента.
    :return: Список доступных платформ в виде словарей с ключами 'id' и 'name'.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT ct.id, ct.name 
                FROM chat_types ct
                LEFT JOIN sessions s ON ct.id = s.chat_type_id AND s.agent_id = %s AND s.is_deleted = FALSE
                WHERE ct.id > 1 AND s.id IS NULL
            """, (agent_id,))
            platforms = cursor.fetchall()
            return platforms
    except Error as e:
        logger.log(f"Ошибка при получении доступных платформ: {e}", "ERROR")
        return []


def add_session(user_id, agent_id, chat_type_id):
    """
    Создаёт новую запись сессии в таблице `sessions`.
    :param user_id: ID пользователя.
    :param agent_id: ID агента.
    :param chat_type_id: ID типа чата.
    :return: ID созданной сессии.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sessions (user_id, agent_id, chat_type_id, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (user_id, agent_id, chat_type_id))
            connection.commit()
            return cursor.lastrowid if cursor.lastrowid else None # Возвращаем ID созданной сессии если он есть иначе None
    except Error as e:
        logger.log(f"Ошибка при создании сессии: {e}", "ERROR")
        return None


def get_all_sessions():
    """
    Извлекает список всех активных сессий.
    :return: Список всех активных сессий.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            query = """
                SELECT 
                    s.id, tb.bot_name, s.created_at, s.updated_at, s.is_active, ct.name AS platform 
                FROM sessions s
                INNER JOIN chat_types ct ON s.chat_type_id = ct.id
                INNER JOIN telegram_bots tb ON s.id = tb.session_id
                WHERE s.is_deleted = FALSE
                ORDER BY s.created_at ASC
            """
            cursor.execute(query)
            sessions = cursor.fetchall()
            return sessions
    except Error as e:
        logger.log(f"Ошибка при получении списка всех сессий: {e}", "ERROR")
        return []


def get_user_sessions(user_id):
    """
    Извлекает список активных сессий для указанного пользователя.
    :param user_id: ID пользователя.
    :return: Список сессий пользователя.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT s.id, s.agent_id, s.chat_type_id, s.is_active, s.created_at, s.updated_at, tb.bot_name, tb.bot_username,
                       a.name AS agent_name, ct.name AS platform
                FROM sessions s
                INNER JOIN gpt_agents a ON s.agent_id = a.id
                INNER JOIN chat_types ct ON s.chat_type_id = ct.id
                INNER JOIN telegram_bots tb ON s.id = tb.session_id
                WHERE s.user_id = %s AND s.is_deleted = FALSE
            """, (user_id,))
            sessions = cursor.fetchall()
            return sessions
    except Error as e:
        logger.log(f"Ошибка при получении сессий пользователя: {e}", "ERROR")
        return []


def get_all_sessions_except_admin(excluded_user_id):
    """
    Извлекает список всех сессий, кроме сессий указанного пользователя.
    :param excluded_user_id: ID пользователя, чьи сессии нужно исключить.
    :return: Список всех сессий, кроме сессий указанного пользователя.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT s.id, s.agent_id, s.chat_type_id, s.is_active, s.created_at, s.updated_at, tb.bot_name, tb.bot_username,
                       a.name AS agent_name, ct.name AS platform, 
                       CASE WHEN u.full_name IS NOT NULL THEN u.full_name ELSE u.username END AS user_name
                FROM sessions s
                INNER JOIN gpt_agents a ON s.agent_id = a.id
                INNER JOIN chat_types ct ON s.chat_type_id = ct.id
                INNER JOIN users u ON s.user_id = u.id
                INNER JOIN telegram_bots tb ON s.id = tb.session_id
                WHERE s.user_id != %s AND s.is_deleted = FALSE
            """, (excluded_user_id,))
            sessions = cursor.fetchall()
            return sessions
    except Error as e:
        logger.log(f"Ошибка при получении всех сессий: {e}", "ERROR")
        return []


def get_all_active_sessions():
    """
    Извлекает список всех активных сессий из базы данных.
    :return: Список активных сессий.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT s.id, s.agent_id, s.chat_type_id, tb.api_token, s.is_active, s.created_at, s.updated_at
                FROM sessions s
                INNER JOIN telegram_bots tb ON s.id = tb.session_id
                WHERE s.is_active = TRUE AND s.is_deleted = FALSE
            """)
            sessions = cursor.fetchall()
            return sessions
    except Error as e:
        logger.log(f"Ошибка при получении активных сессий: {e}", "ERROR")
        return []


def get_session_by_id(session_id):
    """
    Извлекает информацию о сессии по её ID.
    :param session_id: ID сессии.
    :return: Словарь с данными сессии или None, если сессия не найдена.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT s.id, s.agent_id, s.chat_type_id, s.is_active, tb.api_token, tb.webhook_port,
                       s.created_at, s.updated_at, tb.bot_name, tb.bot_username, tb.bot_description, a.name AS agent_name, ct.name AS platform
                FROM sessions s
                INNER JOIN gpt_agents a ON s.agent_id = a.id
                INNER JOIN chat_types ct ON s.chat_type_id = ct.id
                INNER JOIN telegram_bots tb ON s.id = tb.session_id
                WHERE s.id = %s AND s.is_deleted = FALSE
            """, (session_id,))
            session = cursor.fetchone()
            return session
    except Error as e:
        logger.log(f"Ошибка при получении данных сессии: {e}", "ERROR")
        return None


def activate_session_in_db(session_id):
    """
    Активирует сессию в базе данных, устанавливая is_active в TRUE.
    :param session_id: ID сессии.
    :return: True, если сессия успешно активирована, иначе False.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE sessions
                SET is_active = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND is_deleted = FALSE
            """, (session_id,))
            connection.commit()
            return cursor.rowcount > 0  # Возвращает True, если хотя бы одна строка была обновлена
    except Error as e:
        logger.log(f"Ошибка при активации сессии: {e}", "ERROR")
        return False


def terminate_session_in_db(session_id):
    """
    Завершает активную сессию в базе данных, устанавливая is_active в FALSE.
    :param session_id: ID сессии.
    :return: True, если сессия успешно завершена, иначе False.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE sessions
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND is_deleted = FALSE
            """, (session_id,))
            connection.commit()
            return cursor.rowcount > 0  # Возвращает True, если хотя бы одна строка была обновлена
    except Error as e:
        logger.log(f"Ошибка при завершении сессии: {e}", "ERROR")
        return False


####################################### Функции для работы с таблицей "telegram_bots" #######################################

def add_telegram_bot(session_id, api_token, bot_name, bot_username, webhook_port):
    """
    Создаёт новую запись сессии в таблице `sessions`.
    :param session_id: ID сессии.
    :param api_token: API-Токен телеграмм бота.
    :param bot_name: Наименование бота.
    :param bot_username: Username бота.
    :param webhook_port: Порт webhook-а.
    :return: ID созданной сессии.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO telegram_bots (session_id, api_token, bot_name, bot_username, webhook_port, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (session_id, api_token, bot_name, bot_username, webhook_port))
            connection.commit()
    except Error as e:
        logger.log(f"Ошибка при создании телеграм бота: {e}", "ERROR")
        return None


def is_telegram_token_api_exists(api_token):
    """
    Проверяет, существует ли токен в базе данных.

    :param api_token: Токен для проверки.
    :return: True, если токен существует, иначе False.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            query = "SELECT COUNT(*) FROM telegram_bots WHERE api_token = %s"
            cursor.execute(query, (api_token,))
            result = cursor.fetchone()
            return result[0] > 0
    except Error as e:
        logger.log(f"Ошибка при проверке токена: {e}", "ERROR")
        return False


def get_last_webhook_port():
    """
    Возвращает последний использованный порт вебхука в диапазоне от 1 до 65535.

    :return: Последний порт вебхука или None, если порты еще не использовались.
    """
    try:
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(webhook_port) + 1 FROM telegram_bots WHERE webhook_port BETWEEN 1 AND 65535")
            result = cursor.fetchone()
            return result[0]
    except Error as e:
        logger.log(f"Ошибка при получении последнего порта вебхука: {e}", "ERROR")
        return None


def update_bot_name_db(session_id, new_bot_name):
    """
    Обновляет наименование телеграмм бота по его session_id.
    """
    try:
        token = get_session_by_id(session_id)['api_token']
        api_response = update_bot_name(token, new_bot_name)
        if 'Ошибка' in api_response:
            logger.log(f"Ошибка при обновлении имени через API: {api_response}", "ERROR")
            return False
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE telegram_bots SET bot_name = %s WHERE session_id = %s AND is_deleted = FALSE",
                (new_bot_name, session_id)
            )
            connection.commit()
            return True
    except Exception as e:
        logger.log(f"Ошибка при обновлении имени бота в БД: {e}", "ERROR")
        return False


def update_bot_description_db(session_id, new_bot_description):
    """
    Обновляет описание телеграмм бота по его session_id.
    """
    try:
        token = get_session_by_id(session_id)['api_token']
        api_response = update_bot_description(token, new_bot_description)
        if 'Ошибка' in api_response:
            logger.log(f"Ошибка при обновлении описания через API: {api_response}", "ERROR")
            return False
        connection = db_instance.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE telegram_bots SET bot_description = %s WHERE session_id = %s AND is_deleted = FALSE",
                (new_bot_description, session_id)
            )
            connection.commit()
            return True
    except Exception as e:
        logger.log(f"Ошибка при обновлении описания бота в БД: {e}", "ERROR")
        return False


