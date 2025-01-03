"""
db_create_tables.py
Скрипт для создания таблиц в базе данных, необходимых для работы приложения.
Подключается к базе данных, проверяет наличие таблиц и создает их, если они отсутствуют.
"""

from mysql.connector import Error
from db_connection import db_instance


try:
    # Подключение к базе данных через экземпляр Singleton
    connection = db_instance.get_connection()

    if connection.is_connected():
        print("Подключение к базе данных успешно")

        # Создание курсора для выполнения SQL-запросов
        cursor = connection.cursor()

        # Запрос для создания таблицы пользователей
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NULL,
            email VARCHAR(100) NULL,
            phone_number VARCHAR(15) NULL,
            is_admin INT NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT FALSE,        
            UNIQUE INDEX username_UNIQUE (username ASC)
        );
        """
        # Выполнение запроса на создание таблицы users
        cursor.execute(create_table_query)
        print("Таблица 'users' создана или уже существует.")

        # Запрос для создания таблицы агентов
        create_agents_table_query = """
        CREATE TABLE IF NOT EXISTS gpt_agents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name NVARCHAR(50) NOT NULL,
            instruction TEXT,
            start_message TEXT,
            error_message TEXT,
            temperature DECIMAL(2, 1) DEFAULT 0.0 CHECK (temperature <= 1.0),
            max_tokens INT DEFAULT 150,
            message_buffer INT DEFAULT 0,
            accumulate_messages BOOLEAN DEFAULT FALSE,
            transmit_date BOOLEAN DEFAULT FALSE,
            api_key NVARCHAR(255),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
        # Выполнение запроса на создание таблицы gpt_agents
        cursor.execute(create_agents_table_query)
        print("Таблица 'gpt_agents' создана или уже существует.")

        # Запрос для создания таблицы типов чатов
        create_chat_types_table_query = """
        CREATE TABLE IF NOT EXISTS chat_types (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """
        # Выполнение запроса на создание таблицы chat_types
        cursor.execute(create_chat_types_table_query)
        print("Таблица 'chat_types' создана или уже существует.")

        # Запрос для создания таблицы истории чатов
        create_chats_table_query = """
        CREATE TABLE IF NOT EXISTS chats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            agent_id INT NOT NULL,
            chat_type_id INT NOT NULL,
            session_id INT NULL,
            user_message TEXT,
            bot_response TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            response_at DATETIME DEFAULT NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (agent_id) REFERENCES gpt_agents(id),
            FOREIGN KEY (chat_type_id) REFERENCES chat_types(id),
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
        """
        # Выполнение запроса на создание таблицы chats
        cursor.execute(create_chats_table_query)
        print("Таблица 'chats' создана или уже существует.")

        # Таблица для хранения сессий агентов
        create_sessions_table_query = """
       CREATE TABLE IF NOT EXISTS sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            agent_id INT NOT NULL,
            chat_type_id INT NOT NULL,
            user_id INT NOT NULL ,
            is_active BOOLEAN DEFAULT FALSE,
            api_token VARCHAR(255) NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (agent_id) REFERENCES gpt_agents(id),
            FOREIGN KEY (chat_type_id) REFERENCES chat_types(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
        # Выполнение запроса на создание таблицы sessions
        cursor.execute(create_sessions_table_query)
        print("Таблица 'sessions' создана или уже существует.")

except Error as e:
    print(f"Ошибка подключения к базе данных: {e}")

finally:
    # Закрытие соединения и курсора, если соединение активно
    if connection.is_connected():
        cursor.close()
        print("Подключение к базе данных закрыто.")
