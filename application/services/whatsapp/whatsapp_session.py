class WhatsAppSession:
    """Класс для представления одной сессии BAS."""

    def __init__(self, session_id, phone_number, manager):
        self.session_id = session_id
        self.phone_number = phone_number
        self.manager = manager
        self.process_pid = None

    def start(self):
        """Запускает сессию BAS."""
        self.process_pid = self.manager.start_session(self.session_id)
        if not self.process_pid:
            print(f"Ошибка запуска сессии {self.session_id}")
        else:
            print(f"Сессия {self.session_id} успешно запущена (PID: {self.process_pid})")

    def stop(self):
        """Останавливает сессию BAS."""
        if self.process_pid:
            self.manager.stop_session(self.process_pid)
            print(f"Сессия {self.session_id} остановлена.")
