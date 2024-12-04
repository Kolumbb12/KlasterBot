from aiogram.filters import Command  # Импорт фильтра для команд
from aiogram.types import Message
from database.db_functions import select_agent_by_id
from utils.web_clients.gpt_api import generate_response
from utils.logs.logger import logger


async def start_telegram_bot(session_id, bot, dp, stop_flag):
    """
    Запускает Telegram бота с использованием диспетчера и проверяет флаг остановки.
    """
    logger.log(f"Инициализация Telegram бота для сессии {session_id}")
    try:
        # Получаем данные агента
        agent = select_agent_by_id(session_id)
        if not agent:
            logger.log(f"Агент для сессии {session_id} не найден.", "WARNING")
            return

        # Регистрация обработчика команды /start
        async def handle_start(message: Message):
            try:
                logger.log(f"Получена команда /start от пользователя {message.from_user.id}")
                start_message = agent.get('start_message', "Добро пожаловать! Я ваш помощник.")
                await message.answer(start_message)
            except Exception as e:
                error_message = agent.get('error_message', f"Произошла ошибка: {e}. Попробуйте позже.")
                logger.log(f"Ошибка в команде /start: {e}", "ERROR")
                await message.answer(error_message)

        dp.message.register(handle_start, Command(commands=["start"]))
        logger.log(f"Обработчик команды /start зарегистрирован")

        # Регистрация обработчика текстовых сообщений
        async def handle_message(message: Message):
            try:
                user_input = message.text
                logger.log(f"Получено сообщение от пользователя {message.from_user.id}: {user_input}")
                conversation_history = [{"role": "user", "content": user_input}]
                logger.log(f"История пользователя {message.from_user.id}: {conversation_history}")
                response = generate_response(agent_id=agent['id'], user_input=user_input,
                                             conversation_history=conversation_history)
                response = response.encode("utf-8", "ignore").decode("utf-8")
                logger.log(f"Данные сгенерированного ответа: {response}")
                await message.answer(response)
            except Exception as e:
                error_message = agent.get('error_message', f"Произошла ошибка при обработке вашего запроса: {e}")
                logger.log(f"Ошибка при обработке сообщения: {e}", "ERROR")
                await message.answer(error_message)

        dp.message.register(handle_message)
        logger.log(f"Обработчик сообщений зарегистрирован")

        async def handle_any_message(message: Message):
            logger.log(f"Получено сообщение: {message.text} от пользователя {message.from_user.id}", "DEBUG")
            await message.answer("Сообщение принято, но команда не распознана.")

        dp.message.register(handle_any_message)

        # Запуск polling с проверкой флага
        logger.log(f"Запуск polling для Telegram бота сессии {session_id}")
        await dp.start_polling(bot, skip_updates=True)
        logger.log(f"Polling для Telegram бота сессии {session_id} завершен.")
    except Exception as e:
        logger.log(f"Ошибка при запуске Telegram бота для сессии {session_id}: {e}", "ERROR")


async def stop_telegram_bot(session_id, bot, dp, stop_flag):
    """
    Останавливает Telegram бота, завершает polling и закрывает все связанные ресурсы.
    """
    logger.log(f"Остановка Telegram бота для сессии {session_id}")
    try:
        # Устанавливаем флаг остановки
        stop_flag["stop"] = True

        # Останавливаем polling
        await dp.stop_polling()

        # Закрываем соединение с ботом
        await bot.session.close()
        logger.log(f"Сессия Telegram бота для сессии {session_id} закрыта.")
    except Exception as e:
        logger.log(f"Ошибка при остановке Telegram бота для сессии {session_id}: {e}", "ERROR")

