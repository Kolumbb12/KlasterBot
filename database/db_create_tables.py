import mysql.connector
from mysql.connector import Error
from db_connection import create_server_connection


try:
    # Подключение к базе данных
    connection = create_server_connection()

    if connection.is_connected():
        print("Подключение к базе данных успешно")

        # Создание курсора для выполнения SQL-запросов
        cursor = connection.cursor()

        # Пример создания таблицы
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT NOT NULL AUTO_INCREMENT,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_admin INT NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE INDEX username_UNIQUE (username ASC)
        );
        """

        cursor.execute(create_table_query)
        print("Таблица 'users' создана или уже существует.")
except Error as e:
    print(f"Ошибка подключения к базе данных: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Подключение к базе данных закрыто.")