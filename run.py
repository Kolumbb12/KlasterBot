from application.app import create_app


# Инициализация Flask-приложения с использованием функции create_app
app = create_app()


# Запуск сервера
if __name__ == '__main__':

    app.run(debug=True)