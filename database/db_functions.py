"""
db_functions.py
Файл, содержащий функции для работы с таблицами базы данных: users, gpt_agents и chats.
Этот файл предоставляет доступ к данным и позволяет выполнять CRUD операции (создание, чтение, обновление, удаление)
для таблиц, таких как users (пользователи), gpt_agents (агенты GPT) и chats (история чатов).
"""

from mysql.connector import Error
from database.db_connection import db_instance


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
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s AND is_deleted = FALSE", (user_id,))
        user = cursor.fetchone()
        return user
    except Error as e:
        print(f"Ошибка при получении пользователя: {e}")
    finally:
        cursor.close()


def get_all_users():
    """
    Извлекает список всех активных пользователей (которые не были помечены как удаленные).

    :return: Список словарей с данными пользователей (id и username) для каждого активного пользователя.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, username FROM users WHERE is_deleted = FALSE")
        users = cursor.fetchall()
        return users
    except Error as e:
        print(f"Ошибка при получении списка пользователей: {e}")
    finally:
        cursor.close()


def insert_user(username, password, is_admin=0):
    """
    Вставляет нового пользователя в базу данных с указанными именем пользователя, паролем и статусом администратора.

    :param username: Имя нового пользователя (уникальное).
    :param password: Пароль нового пользователя.
    :param is_admin: Флаг, указывающий, является ли пользователь администратором (0 - нет, 1 - да).
    :raises ValueError: Если имя пользователя уже занято, вызывает исключение с сообщением об ошибке.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)",
            (username, password, is_admin)
        )
        connection.commit()
        print("Пользователь успешно добавлен.")
    except Error as e:
        if "Duplicate entry" in str(e):
            raise ValueError("Пользователь с таким именем уже существует.")
        else:
            raise e
    finally:
        cursor.close()


def update_user_password(user_id, new_password):
    """
    Обновляет пароль пользователя по его ID.

    :param user_id: ID пользователя, пароль которого нужно обновить.
    :param new_password: Новый пароль пользователя.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s AND is_deleted = FALSE",
            (new_password, user_id)
        )
        connection.commit()
        print("Пароль пользователя обновлен.")
    except Error as e:
        print(f"Ошибка при обновлении пароля: {e}")
    finally:
        cursor.close()


def delete_user(user_id):
    """
    Помечает пользователя как удаленного (soft delete) по его ID.

    :param user_id: ID пользователя, которого нужно пометить как удаленного.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET is_deleted = TRUE WHERE id = %s", (user_id,))
        connection.commit()
        print("Пользователь удален.")
    except Error as e:
        print(f"Ошибка при удалении пользователя: {e}")
    finally:
        cursor.close()


def update_user_profile(user_id, settings):
    """
    Обновляет профиль пользователя. Доступные для обновления поля включают полное имя, email, телефон и пароль.

    :param user_id: ID пользователя, профиль которого нужно обновить.
    :param settings: Словарь с ключами и значениями для обновления (например, {'full_name': 'Иванов Иван Иванович'}).
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor()

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
            print("Профиль пользователя обновлен.")
        else:
            print("Нет допустимых полей для обновления.")
    except Error as e:
        print(f"Ошибка при обновлении профиля пользователя: {e}")
    finally:
        cursor.close()


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
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gpt_agents WHERE id = %s AND is_deleted = FALSE", (agent_id,))
        agent = cursor.fetchone()
        return agent
    except Error as e:
        print(f"Ошибка при получении агента: {e}")
    finally:
        cursor.close()


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
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO gpt_agents (user_id, name, instruction, start_message, error_message, temperature, max_tokens, message_buffer, accumulate_messages, transmit_date, api_key) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_id, name, instruction, start_message, error_message, temperature, max_tokens, message_buffer,
             accumulate_messages, transmit_date, api_key)
        )
        connection.commit()
        print("Агент успешно добавлен.")
    except Error as e:
        print(f"Ошибка при добавлении агента: {e}")
    finally:
        cursor.close()


def select_all_agents_by_user_id(user_id):
    """
    Извлекает всех агентов, связанных с конкретным пользователем, из базы данных.

    :param user_id: ID пользователя, для которого нужно получить агентов.
    :return: Список агентов, принадлежащих пользователю, в формате словаря.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gpt_agents WHERE user_id = %s AND is_deleted = FALSE", (user_id,))
        agents = cursor.fetchall()
        return agents
    except Error as e:
        print(f"Ошибка при получении агентов пользователя: {e}")
    finally:
        cursor.close()


def update_agent_settings(agent_id, settings):
    """
    Обновляет настройки агента в базе данных для указанного агентского ID.

    :param agent_id: ID агента, для которого нужно обновить настройки.
    :param settings: Словарь с полями и их новыми значениями для обновления.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor()

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
            print("Настройки агента обновлены.")
        else:
            print("Нет допустимых полей для обновления.")
    except Error as e:
        print(f"Ошибка при обновлении настроек агента: {e}")
    finally:
        cursor.close()


def set_agent_active_status(agent_id, is_active):
    """
    Изменяет статус активности агента.

    :param agent_id: ID агента, для которого нужно изменить статус.
    :param is_active: Новое значение статуса активности (True или False).
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE gpt_agents SET is_active = %s WHERE id = %s AND is_deleted = FALSE",
            (is_active, agent_id)
        )
        connection.commit()
    except Error as e:
        print(f"Ошибка при изменении статуса агента: {e}")
    finally:
        cursor.close()

######################################### Функции для работы таблицей с "chats" ########################################

def select_chat_by_id(chat_id):
    """
    Извлекает данные чата по его ID.

    :param chat_id: ID чата.
    :return: Словарь с данными чата (пользовательские и бот-сообщения), если чат существует.
    Возвращает None, если чат не найден.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM chats WHERE id = %s AND is_deleted = FALSE", (chat_id,))
        chat = cursor.fetchone()
        return chat
    except Error as e:
        print(f"Ошибка при получении чата: {e}")
    finally:
        cursor.close()

def get_chat_history_by_user_and_agent(user_id, agent_id, chat_type_id):
    """
    Извлекает историю чата для заданного пользователя, агента и типа чата.

    :param user_id: ID пользователя, чья история чата требуется.
    :param agent_id: ID агента, связанного с этим чатом.
    :param chat_type_id: ID типа чата (например, 1 - тестовый чат).
    :return: Список словарей с сообщениями чата, где каждое сообщение включает роль (user или assistant) и текст сообщения (content).
             Если история пуста, возвращается пустой список.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor(dictionary=True)
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
        print(f"Ошибка при чтении истории чата: {e}")
    finally:
        cursor.close()


def get_chat_history_by_session(session_id):
    """
    Извлекает историю чата для заданной сессии в Telegram.

    :param session_id: ID сессии, для которой требуется история чата.
    :return: Список словарей с сообщениями чата, где каждое сообщение включает роль (user или assistant) и текст сообщения (content).
             Если история пуста, возвращается пустой список.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT user_message, bot_response 
        FROM chats
        WHERE session_id = %s AND is_deleted = FALSE
        ORDER BY created_at
        """
        cursor.execute(query, (session_id,))
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
        print(f"Ошибка при чтении истории чата: {e}")
    finally:
        cursor.close()


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
        cursor = connection.cursor(dictionary=True)
        query = """
        INSERT INTO chats (user_id, agent_id, chat_type_id, user_message, bot_response)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, agent_id, chat_type_id, user_message, bot_response))
        connection.commit()
    except Error as e:
        print(f"Ошибка при записи истории чата: {e}")
    finally:
        cursor.close()


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
        cursor = connection.cursor(dictionary=True)
        query = """
        INSERT INTO chats (user_id, agent_id, chat_type_id, session_id, user_message, bot_response)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, agent_id, chat_type_id, session_id, user_message, bot_response))
        connection.commit()
    except Error as e:
        print(f"Ошибка при записи истории чата: {e}")
    finally:
        cursor.close()


def delete_chat_history(user_id, agent_id, chat_type_id):
    """
    Помечает все сообщения чата как удаленные (soft delete) для заданного пользователя, агента и типа чата.

    :param user_id: ID пользователя, для которого необходимо очистить историю чата.
    :param agent_id: ID агента, связанного с этим чатом.
    :param chat_type_id: ID типа чата.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE chats 
            SET is_deleted = TRUE 
            WHERE user_id = %s AND agent_id = %s AND chat_type_id = %s
        """, (user_id, agent_id, chat_type_id))
        connection.commit()
        print("История чата успешно удалена.")
    except Error as e:
        print(f"Ошибка при удалении истории чата: {e}")
    finally:
        cursor.close()

####################################### Функции для работы с таблицей "sessions" #######################################

def get_available_platforms(agent_id):
    """
    Извлекает список доступных платформ для агента, исключая те, для которых сессии уже созданы.

    :param agent_id: ID агента.
    :return: Список доступных платформ в виде словарей с ключами 'id' и 'name'.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT ct.id, ct.name 
            FROM chat_types ct
            LEFT JOIN sessions s ON ct.id = s.chat_type_id AND s.agent_id = %s AND s.is_deleted = FALSE
            WHERE ct.id > 1 AND s.id IS NULL
        """, (agent_id,))
        platforms = cursor.fetchall()
        return platforms
    except Error as e:
        print(f"Ошибка при получении доступных платформ: {e}")
        return []
    finally:
        cursor.close()


def add_session(user_id, agent_id, chat_type_id, api_token):
    """
    Создаёт новую запись сессии в таблице `sessions`.
    :param user_id: ID пользователя.
    :param agent_id: ID агента.
    :param chat_type_id: ID типа чата.
    :param api_token: Токен бота.
    :return: ID созданной сессии.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO sessions (user_id, agent_id, chat_type_id, api_token, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (user_id, agent_id, chat_type_id, api_token))
        connection.commit()
        return cursor.lastrowid  # Возвращаем ID созданной сессии
    except Error as e:
        print(f"Ошибка при создании сессии: {e}")
        return None
    finally:
        cursor.close()


def get_user_sessions(user_id):
    """
    Извлекает список активных сессий для указанного пользователя.
    :param user_id: ID пользователя.
    :return: Список сессий пользователя.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.id, s.agent_id, s.chat_type_id, s.is_active, s.created_at, s.updated_at, 
                   a.name AS agent_name, ct.name AS platform
            FROM sessions s
            INNER JOIN gpt_agents a ON s.agent_id = a.id
            INNER JOIN chat_types ct ON s.chat_type_id = ct.id
            WHERE s.user_id = %s AND s.is_deleted = FALSE
        """, (user_id,))
        sessions = cursor.fetchall()
        return sessions
    except Error as e:
        print(f"Ошибка при получении сессий пользователя: {e}")
        return []
    finally:
        cursor.close()


def get_all_active_sessions():
    """
    Извлекает список всех активных сессий из базы данных.
    :return: Список активных сессий.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, agent_id, chat_type_id, api_token, is_active, created_at, updated_at
            FROM sessions
            WHERE is_active = TRUE AND is_deleted = FALSE
        """)
        sessions = cursor.fetchall()
        return sessions
    except Error as e:
        print(f"Ошибка при получении активных сессий: {e}")
        return []
    finally:
        cursor.close()


def get_session_by_id(session_id):
    """
    Извлекает информацию о сессии по её ID.
    :param session_id: ID сессии.
    :return: Словарь с данными сессии или None, если сессия не найдена.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.id, s.agent_id, s.chat_type_id, s.is_active, s.api_token, 
                   s.created_at, s.updated_at, a.name AS agent_name, ct.name AS platform
            FROM sessions s
            INNER JOIN gpt_agents a ON s.agent_id = a.id
            INNER JOIN chat_types ct ON s.chat_type_id = ct.id
            WHERE s.id = %s AND s.is_deleted = FALSE
        """, (session_id,))
        session = cursor.fetchone()
        return session
    except Error as e:
        print(f"Ошибка при получении данных сессии: {e}")
        return None
    finally:
        cursor.close()


def activate_session_in_db(session_id):
    """
    Активирует сессию в базе данных, устанавливая is_active в TRUE.
    :param session_id: ID сессии.
    :return: True, если сессия успешно активирована, иначе False.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE sessions
            SET is_active = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND is_deleted = FALSE
        """, (session_id,))
        connection.commit()
        return cursor.rowcount > 0  # Возвращает True, если хотя бы одна строка была обновлена
    except Error as e:
        print(f"Ошибка при активации сессии: {e}")
        return False
    finally:
        cursor.close()


def terminate_session_in_db(session_id):
    """
    Завершает активную сессию в базе данных, устанавливая is_active в FALSE.
    :param session_id: ID сессии.
    :return: True, если сессия успешно завершена, иначе False.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE sessions
            SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND is_deleted = FALSE
        """, (session_id,))
        connection.commit()
        return cursor.rowcount > 0  # Возвращает True, если хотя бы одна строка была обновлена
    except Error as e:
        print(f"Ошибка при завершении сессии: {e}")
        return False
    finally:
        cursor.close()


def get_telegram_bot_token_api_by_session_id(session_id):
    """
    Извлекает токен API Telegram бота из базы данных по session_id.
    :param session_id: ID сессии.
    :return: Токен API, если найден, иначе None.
    """
    try:
        connection = db_instance.get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT api_token
            FROM sessions
            WHERE id = %s AND is_deleted = FALSE
        """, (session_id,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Возвращаем значение из первой колонки (api_token)
        else:
            return None
    except Error as e:
        print(f"Ошибка при извлечении токена API для сессии {session_id}: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
