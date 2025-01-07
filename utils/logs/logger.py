import logging
import threading
import traceback
import os
import inspect
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()


class Logger:

    def __init__(self, log_file=os.getenv("LOGS_PATH")):
        self.lock = threading.Lock()  # Для управления доступом
        self.log_file = log_file

    def log(self, message, level="INFO", exc_info=None):
        """
        Записывает лог-сообщение в файл.
        :param message: Текст сообщения
        :param level: Уровень логирования (INFO, DEBUG, WARNING, ERROR, CRITICAL)
        :param exc_info: Информация об исключении (опционально)
        """
        with self.lock:  # Потоко-безопасная запись
            # Получаем данные о месте вызова
            caller_frame = inspect.stack()[1]
            filename = os.path.basename(caller_frame.filename)
            func_name = caller_frame.function if caller_frame.function != "<module>" else "main"
            line_number = caller_frame.lineno
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

            # Добавляем информацию об ошибке, если она есть
            if exc_info:
                error_message = traceback.format_exception(None, exc_info, exc_info.__traceback__)
                message += f" | Error: {''.join(error_message).strip()}"

            # Формируем строку лога
            log_entry = f"{current_time}:{filename}:{func_name}:{line_number}:{level}:{message}"

            # Записываем в файл
            with open(self.log_file, "a", encoding="utf-8") as file:
                file.write(log_entry + "\n")


logger = Logger()
