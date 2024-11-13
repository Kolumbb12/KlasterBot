import mysql.connector
from mysql.connector import Error as sqlError
from dotenv import load_dotenv
import os


load_dotenv()


class DatabaseConnection:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        """Инициализирует соединение с базой данных"""
        try:
            self._connection = mysql.connector.connect(
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                database=os.getenv('DB_NAME')
            )
            print("Соединение с базой данных успешно установлено.")
        except sqlError as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            self._connection = None

    def get_connection(self):
        """Возвращает текущее соединение. Если оно потеряно, переподключается."""
        try:
            if self._connection is None or not self._connection.is_connected():
                print("Переподключение к базе данных...")
                self._initialize_connection()
            return self._connection
        except sqlError as e:
            print(f"Ошибка при проверке соединения: {e}")
            self._initialize_connection()
            return self._connection

    def close_connection(self):
        """Закрывает соединение с базой данных."""
        if self._connection is not None and self._connection.is_connected():
            self._connection.close()
            print("Соединение с базой данных закрыто.")

    @classmethod
    def teardown(cls):
        """Метод для полного закрытия соединения, вызывается в конце работы приложения"""
        if cls._instance:
            cls._instance.close_connection()
            cls._instance = None
            print("Синглтон соединения с базой данных успешно завершён.")


db_instance = DatabaseConnection()