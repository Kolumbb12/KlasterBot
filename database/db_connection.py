"""
db_connection.py
Модуль для установки и управления соединением с базой данных.
Реализует паттерн Singleton для обеспечения единственного экземпляра соединения в приложении,
чтобы предотвратить избыточные подключения и улучшить производительность.
"""

import mysql.connector
from mysql.connector import Error as sqlError
from dotenv import load_dotenv
import os


# Загружаем переменные окружения из .env файла
load_dotenv()


class DatabaseConnection:
    """
    Класс для управления соединением с базой данных.
    Использует Singleton для поддержания одного соединения в течение всего времени работы приложения.
    """
    _instance = None  # Единственный экземпляр класса DatabaseConnection
    _connection = None  # Объект соединения с базой данных

    def __new__(cls):
        """
        Создает и возвращает единственный экземпляр класса.
        При первом вызове также инициирует соединение с базой данных.

        :return: Экземпляр класса DatabaseConnection
        :rtype: DatabaseConnection
        """
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        """
        Инициализирует соединение с базой данных, используя параметры подключения из переменных окружения.
        Выводит сообщение об успешном подключении или ошибке в случае неудачи.
        """
        try:
            user = os.getenv('DB_USER')
            password = os.getenv('DB_PASSWORD')
            host = os.getenv('DB_HOST')
            database = os.getenv('DB_NAME')

            self._connection = mysql.connector.connect(
                user=user,
                password=password,
                host=host,
                database=database
            )
            print("Соединение с базой данных успешно установлено.")
        except sqlError as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            self._connection = None

    def get_connection(self):
        """
        Возвращает текущее соединение с базой данных. Если соединение потеряно, пытается переподключиться.

        :return: Соединение с базой данных или None в случае ошибки
        :rtype: mysql.connector.connection.MySQLConnection or None
        """
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
        """
        Закрывает текущее соединение с базой данных, если оно активно. Выводит сообщение о закрытии соединения.
        """
        if self._connection is not None and self._connection.is_connected():
            self._connection.close()
            print("Соединение с базой данных закрыто.")

    @classmethod
    def teardown(cls):
        """
        Полностью закрывает соединение и сбрасывает экземпляр Singleton.
        Используется для завершения соединения в конце работы приложения.
        """
        if cls._instance:
            cls._instance.close_connection()
            cls._instance = None
            print("Синглтон соединения с базой данных успешно завершены.")


# Экземпляр DatabaseConnection для использования во всем приложении
db_instance = DatabaseConnection()
