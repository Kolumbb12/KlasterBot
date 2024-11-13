from application.app import create_app
from database.db_connection import db_instance
import atexit


# Инициализация Flask-приложения с использованием функции create_app
app = create_app()

# Запуск сервера
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    atexit.register(db_instance.teardown)
