from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat

from models import Message
from config import GIGA_AUTH_KEY


# Авторизация в сервисе GigaChat
chat = GigaChat(credentials=GIGA_AUTH_KEY, verify_ssl_certs=False)


def generate_system_prompt(characters, main_idea):
    prompt = f"""
    Ты - бот для рассказа сказок.
    Тебе подают запрос на основе которого ты придумываешь сказку или дальнейшее развитие событий в сказке
    Рассказывай сказку на основе следующих данных:
    Персонажи: {characters}
    Основная идея: {main_idea}
    В конце каждого ответа спрашивай: Что было дальше?.
    """
    return prompt


def ask_gigachat(chat_id, prompt, sys_prompt):
    try:
        global chat
        messages = [SystemMessage(content=sys_prompt)]

        for message in Message.query.filter_by(user_id=chat_id).order_by(Message.timestamp).all():
            messages.append(HumanMessage(content=message.content))

        messages.append(HumanMessage(content=prompt))
        res = chat(messages)
        return res.content
    except Exception as e:
        return str(e)
