"""
gpt_api.py
Модуль взаимодействия с API OpenAI для генерации ответов на основе истории диалога.
Используется для получения ответов от модели на основе инструкций агента и введенных данных пользователя.
"""

import openai

from database.db_functions import get_agent_by_id
from utils.utils import convert_decimals
from utils.logs.logger import logger


def get_openai_api_key(agent_id):
    """
    Получает API-ключ для указанного агента.

    :param agent_id: Идентификатор агента, для которого требуется получить API-ключ.
    :return: API-ключ, если он существует для агента.
    :raises ValueError: Если API-ключ не найден для указанного агента.
    """
    agent = get_agent_by_id(agent_id)
    if agent and agent['api_key']:
        return agent['api_key']
    else:
        raise ValueError("API-ключ не найден для указанного агента.")


from datetime import datetime

def generate_response(agent_id, user_input, conversation_history):
    """
    Генерирует ответ на основе истории диалога и введенных данных пользователя, используя OpenAI API.

    :param agent_id: Идентификатор агента, для которого выполняется запрос.
    :param user_input: Введенные данные пользователя, на которые требуется ответить.
    :param conversation_history: История диалога, включающая предыдущие сообщения пользователя и ответы бота.
    :return: Ответ модели в виде строки.
    :raises ValueError: Если агент не найден или отсутствует API-ключ.
    """
    try:
        # Получаем данные агента
        agent = get_agent_by_id(agent_id)
        if not agent:
            logger.log(f"Ошибка: Агент с ID {agent_id} не найден.", level="ERROR")
            raise ValueError("Агент не найден.")
        # logger.log(f"Получены данные агента: {agent}")
        # Устанавливаем API-ключ для OpenAI
        openai.api_key = get_openai_api_key(agent_id)
        # logger.log(f"API-ключ для агента {agent_id} успешно установлен.")
        # Преобразуем инструкцию и параметры агента
        prompt = convert_decimals(agent['instruction'])
        temperature = convert_decimals(agent['temperature'])
        max_tokens = agent['max_tokens']
        # logger.log(f"Параметры агента: prompt={prompt}, temperature={temperature}, max_tokens={max_tokens}")
        # Обработка пользовательского ввода
        user_input = str(user_input).encode("utf-8").decode("utf-8")
        # logger.log(f"Входное сообщение пользователя: {user_input}")
        # Преобразуем conversation_history, убирая объекты datetime
        formatted_conversation_history = []
        for msg in conversation_history:
            formatted_msg = msg.copy()
            if isinstance(formatted_msg.get('created_at'), datetime):
                formatted_msg['created_at'] = formatted_msg['created_at'].isoformat()  # Преобразуем datetime в строку
            formatted_conversation_history.append(formatted_msg)
        # Формируем историю сообщений для OpenAI API
        messages = [{"role": "system", "content": prompt}] + formatted_conversation_history + [{"role": "user", "content": user_input}]
        # logger.log(f"История сообщений для OpenAI API: {messages}")
        # Выполняем запрос к OpenAI API для генерации ответа
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        # logger.log(f"Ответ от OpenAI API: {response}")
        # Извлекаем ответ и преобразуем его к нужному формату
        response_data = {
            "response": response.choices[0].message['content']
        }
        response_data = convert_decimals(response_data)
        response_data['response'] = str(response_data['response']).encode("utf-8").decode("utf-8")
        # logger.log(f"Сформированный ответ: {response_data['response']}")
        return response_data['response']

    except Exception as e:
        logger.log(f"Ошибка в generate_response: {e}", level="ERROR")
        raise


def validate_api_key(api_key):
    """
    Проверяет валидность переданного API-ключа путем выполнения тестового запроса к OpenAI API.

    :param api_key: API-ключ для проверки.
    :return: True, если ключ валиден, иначе False.
    """
    openai.api_key = api_key
    try:
        openai.Model.list()
        return True
    except openai.error.AuthenticationError:
        return False
    except Exception as e:
        logger.log(f"Ошибка при проверке GPT API KEY: {e}")
        return False