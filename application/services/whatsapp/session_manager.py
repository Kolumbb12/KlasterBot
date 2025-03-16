import subprocess
import time
import psutil
import win32gui
import win32con
import win32api
from threading import Lock


class WhatsAppSessionManager:
    """Класс для управления процессами BAS (WhatsAppSession)."""

    task_name = "WhatsAppSessionAutoRun"  # Название задачи в планировщике Windows
    exe_name = "FastExecuteScript.exe"  # Исполняемый файл BAS
    window_title = "WhatsAppSession(1.0.0)"  # Название окна BAS

    def __init__(self):
        self.lock = Lock()

    def start_session(self, session_id):
        """Запускает новую сессию BAS для WhatsApp."""
        with self.lock:
            subprocess.run(
                ["schtasks", "/run", "/tn", self.task_name],
                shell=True,
                capture_output=True,
                text=True,
                encoding="cp1251"
            )

            # Ожидаем появления процесса
            process_pid = self._wait_for_process()
            if not process_pid:
                return None

            # Ждём загрузки окна и нажимаем "ОК"
            time.sleep(3)
            self._handle_window()
            return process_pid

    def _wait_for_process(self, timeout=15):
        """Ожидает, пока появится процесс BAS."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            for proc in psutil.process_iter(attrs=['pid', 'name']):
                if self.exe_name.lower() in proc.info['name'].lower():
                    print(f"Процесс {self.exe_name} найден! PID: {proc.info['pid']}")
                    return proc.info['pid']
            time.sleep(1)
        print("Ошибка: процесс не найден!")
        return None

    def _handle_window(self):
        """Находит и нажимает кнопку 'ОК' в BAS."""
        hwnd = win32gui.FindWindow(None, self.window_title)
        if hwnd:
            print(f"Фокусируемся на окне: {self.window_title}")
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(1)
            win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
            win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
            print("Нажатие 'ОК' выполнено!")

    def stop_session(self, process_pid):
        """Закрывает процесс BAS."""
        for proc in psutil.process_iter():
            if proc.pid == process_pid:
                proc.terminate()
                print(f"Процесс {self.exe_name} (PID: {process_pid}) завершён.")
                break
