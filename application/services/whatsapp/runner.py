# """
# runner.py
# Модуль для управления WhatsApp-ботами через Twilio API.
# """
#
# import os
# from twilio.rest import Client
# from dotenv import load_dotenv
#
# # Загрузка переменных окружения из .env файла
# load_dotenv()
#
#
# class WhatsAppBotRunner:
#     def __init__(self, session_id, phone_number):
#         """
#         Инициализация WhatsApp-бота через Twilio API.
#
#         :param session_id: Идентификатор сессии
#         :param phone_number: Номер телефона, связанный с ботом
#         """
#         self.session_id = session_id
#         self.phone_number = phone_number
#         self.client = Client(
#             os.getenv("TWILIO_ACCOUNT_SID"),
#             os.getenv("TWILIO_AUTH_TOKEN")
#         )
#         self.twilio_number = os.getenv("TWILIO_PHONE_NUMBER")  # Получение Twilio номера из переменных окружения
#         self.webhook_url = f"{os.getenv('NGROK_ADDRESS')}/webhook/{self.session_id}"
#
#     async def start_webhook(self):
#         """
#         Устанавливает Webhook в Twilio для приема сообщений.
#         """
#         try:
#             self.client.messages.create(
#                 from_=f"whatsapp:{self.twilio_number}",
#                 to=f"whatsapp:{self.phone_number}",
#                 body=f"Webhook активирован на {self.webhook_url}"
#             )
#
#             print(f"Webhook для номера {self.phone_number} установлен: {self.webhook_url}")
#         except Exception as e:
#             print(f"Ошибка при установке Webhook для {self.phone_number}: {e}")
#
#     async def stop_webhook(self):
#         """
#         Удаляет Webhook из Twilio (Sandbox не поддерживает явное удаление, здесь логируем).
#         """
#         try:
#             print(f"Webhook для номера {self.phone_number} остановлен.")
#         except Exception as e:
#             print(f"Ошибка при удалении Webhook: {e}")
#
#     def send_message(self, to, message):
#         """
#         Отправляет сообщение через Twilio API.
#
#         :param to: Номер получателя в формате "whatsapp:+номер"
#         :param message: Текст сообщения
#         """
#         try:
#             response = self.client.messages.create(
#                 from_=f"whatsapp:{self.twilio_number}",
#                 to=f"whatsapp:{to}",
#                 body=message
#             )
#             print(f"Сообщение отправлено на {to}: SID {response.sid}")
#         except Exception as e:
#             print(f"Ошибка отправки сообщения: {e}")
#
#     def get_bot_status(self):
#         """
#         Проверяет статус соединения с Twilio.
#         """
#         try:
#             balance = self.client.api.v2010.balance.fetch()
#             return f"Текущий баланс: {balance.balance} {balance.currency}"
#         except Exception as e:
#             return f"Ошибка получения статуса бота: {e}"
#
#
# # Пример использования (для тестирования)
# if __name__ == "__main__":
#     session_id = 24  # Пример идентификатора сессии
#     phone_number = "+77053911151"  # Замените на реальный номер
#
#     bot = WhatsAppBotRunner(session_id, phone_number)
#     bot.send_message(phone_number, "Привет! Это тестовое сообщение от бота.")
