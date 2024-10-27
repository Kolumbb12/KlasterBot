import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

def create_server_connection():
    """Подключение к серверу MySQL без указания конкретной базы данных."""
    try:
        connection = mysql.connector.connect(
            user=os.getenv('DB_USER'),            # Ваш MySQL username
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),         # Локальный хост, если MySQL на локальной машине
            database=os.getenv('DB_NAME')
        )
        if connection.is_connected():
            print("Подключение к серверу MySQL успешно")
        return connection
    except Error as e:
        print(f"Ошибка подключения к серверу MySQL: {e}")
        return None

def create_database(connection, query):
    """Выполнение запроса для создания базы данных."""
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("База данных создана успешно")
    except Error as e:
        print(f"Ошибка создания базы данных: {e}")

# Вызываем функцию для создания базы данных
if __name__ == "__main__":
    connection = create_server_connection()
    if connection:
        create_database_query = "CREATE DATABASE klasterbot_db"
        create_database(connection, create_database_query)
        connection.close()