import openai
from database.db_functions import select_agent_by_id
from application.utils import convert_decimals


def get_openai_api_key(agent_id):
    agent = select_agent_by_id(agent_id)
    if agent and agent['api_key']:
        return agent['api_key']
    else:
        raise ValueError("API-ключ не найден для указанного агента.")


def generate_response(agent_id, user_input, conversation_history):
    agent = select_agent_by_id(agent_id)
    if not agent:
        raise ValueError("Агент не найден.")

    openai.api_key = get_openai_api_key(agent_id)

    prompt = convert_decimals(agent['instruction'])
    temperature = convert_decimals(agent['temperature'])
    max_tokens = agent['max_tokens']

    # Формируем историю для отправки
    messages = [{"role": "system", "content": prompt}] + conversation_history + [{"role": "user", "content": user_input}]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

    response_data = {
        "response": response.choices[0].message['content']
    }

    response_data = convert_decimals(response_data)
    return response_data['response']