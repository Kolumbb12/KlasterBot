"""
gpt_api.py
Модуль взаимодействия с API OpenAI для генерации ответов на основе истории диалога.
Используется для получения ответов от модели на основе инструкций агента и введенных данных пользователя.
"""

import openai
from database.db_functions import select_agent_by_id
from utils.utils import convert_decimals
from utils.logs.logger import logger


def get_openai_api_key(agent_id):
    """
    Получает API-ключ для указанного агента.

    :param agent_id: Идентификатор агента, для которого требуется получить API-ключ.
    :return: API-ключ, если он существует для агента.
    :raises ValueError: Если API-ключ не найден для указанного агента.
    """
    agent = select_agent_by_id(agent_id)
    if agent and agent['api_key']:
        return agent['api_key']
    else:
        raise ValueError("API-ключ не найден для указанного агента.")


def generate_response(agent_id, user_input, conversation_history):
    """
    Генерирует ответ на основе истории диалога и введенных данных пользователя, используя OpenAI API.

    :param agent_id: Идентификатор агента, для которого выполняется запрос.
    :param user_input: Введенные данные пользователя, на которые требуется ответить.
    :param conversation_history: История диалога, включающая предыдущие сообщения пользователя и ответы бота.
    :return: Ответ модели в виде строки.
    :raises ValueError: Если агент не найден или отсутствует API-ключ.
    """
    # Получаем данные агента
    agent = select_agent_by_id(agent_id)
    if not agent:
        raise ValueError("Агент не найден.")

    # Устанавливаем API-ключ для OpenAI
    openai.api_key = get_openai_api_key(agent_id)

    # Преобразуем инструкцию и параметры агента
    prompt = convert_decimals(agent['instruction'])
    temperature = convert_decimals(agent['temperature'])
    max_tokens = agent['max_tokens']

    user_input = str(user_input).encode("utf-8").decode("utf-8")  # Убедимся в корректной кодировке

    # Формируем историю сообщений для OpenAI API
    messages = [{"role": "system", "content": prompt}] + conversation_history + [{"role": "user", "content": user_input}]

    # Выполняем запрос к OpenAI API для генерации ответа
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

    # Извлекаем ответ и преобразуем его к нужному формату
    response_data = {
        "response": response.choices[0].message['content']
    }
    # Преобразуем возможные значения Decimal в float для предотвращения ошибок
    response_data = convert_decimals(response_data)

    response_data['response'] = str(response_data['response']).encode("utf-8").decode("utf-8")  # Убедимся в корректной кодировке

    logger.log(f"Данные сгенерированного ответа: {response_data['response']}")

    return response_data['response']
