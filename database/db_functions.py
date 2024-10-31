from mysql.connector import Error
from database.db_connection import create_server_connection


# Функции для таблицы users
def select_user_by_id(user_id):
    try:
        connection = create_server_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s AND is_deleted = FALSE", (user_id,))
        user = cursor.fetchone()
        return user
    except Error as e:
        print(f"Ошибка при получении пользователя: {e}")
    finally:
        cursor.close()
        connection.close()


def insert_user(username, password, is_admin=0):
    try:
        connection = create_server_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)",
            (username, password, is_admin)
        )
        connection.commit()
        print("Пользователь успешно добавлен.")
    except Error as e:
        print(f"Ошибка при добавлении пользователя: {e}")
    finally:
        cursor.close()
        connection.close()


def update_user_password(user_id, new_password):
    try:
        connection = create_server_connection()
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
        connection.close()


def delete_user(user_id):
    try:
        connection = create_server_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET is_deleted = TRUE WHERE id = %s", (user_id,))
        connection.commit()
        print("Пользователь удален.")
    except Error as e:
        print(f"Ошибка при удалении пользователя: {e}")
    finally:
        cursor.close()
        connection.close()


# Функции для таблицы gpt_agents
def select_agent_by_id(agent_id):
    try:
        connection = create_server_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gpt_agents WHERE id = %s AND is_deleted = FALSE", (agent_id,))
        agent = cursor.fetchone()
        return agent
    except Error as e:
        print(f"Ошибка при получении агента: {e}")
    finally:
        cursor.close()
        connection.close()


def insert_agent(user_id, name, instruction, temperature=0.5, max_tokens=150, message_buffer=0, accumulate_messages=False, transmit_date=False, api_key=None):
    try:
        connection = create_server_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO gpt_agents (user_id, name, instruction, temperature, max_tokens, message_buffer, accumulate_messages, transmit_date, api_key) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_id, name, instruction, temperature, max_tokens, message_buffer, accumulate_messages, transmit_date, api_key)
        )
        connection.commit()
        print("Агент успешно добавлен.")
    except Error as e:
        print(f"Ошибка при добавлении агента: {e}")
    finally:
        cursor.close()
        connection.close()


def select_all_agents_by_user_id(user_id):
    try:
        connection = create_server_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gpt_agents WHERE user_id = %s AND is_deleted = FALSE", (user_id,))
        agents = cursor.fetchall()
        return agents
    except Error as e:
        print(f"Ошибка при получении агентов пользователя: {e}")
    finally:
        cursor.close()
        connection.close()


def update_agent_settings(agent_id, settings):
    try:
        connection = create_server_connection()
        cursor = connection.cursor()

        # Формируем динамический запрос SQL
        update_fields = []
        values = []
        for field, value in settings.items():
            if field not in ('created_at', 'is_active'):
                update_fields.append(f"{field} = %s")
                values.append(value)

        # Если есть поля для обновления
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
        connection.close()


def set_agent_active_status(agent_id, is_active):
    try:
        connection = create_server_connection()
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
        connection.close()


def delete_agent(agent_id):
    try:
        connection = create_server_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE gpt_agents SET is_deleted = TRUE WHERE id = %s", (agent_id,))
        connection.commit()
        print("Агент удален.")
    except Error as e:
        print(f"Ошибка при удалении агента: {e}")
    finally:
        cursor.close()
        connection.close()


# Функции для таблицы chats
def select_chat_by_id(chat_id):
    try:
        connection = create_server_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM chats WHERE id = %s AND is_deleted = FALSE", (chat_id,))
        chat = cursor.fetchone()
        return chat
    except Error as e:
        print(f"Ошибка при получении чата: {e}")
    finally:
        cursor.close()
        connection.close()


def insert_chat(user_id, agent_id, user_message, bot_response=None):
    try:
        connection = create_server_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO chats (user_id, agent_id, user_message, bot_response) VALUES (%s, %s, %s, %s)",
            (user_id, agent_id, user_message, bot_response)
        )
        connection.commit()
        print("Чат добавлен.")
    except Error as e:
        print(f"Ошибка при добавлении чата: {e}")
    finally:
        cursor.close()
        connection.close()


def delete_chat(chat_id):
    try:
        connection = create_server_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE chats SET is_deleted = TRUE WHERE id = %s", (chat_id,))
        connection.commit()
        print("Чат удален.")
    except Error as e:
        print(f"Ошибка при удалении чата: {e}")
    finally:
        cursor.close()
        connection.close()
