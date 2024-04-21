from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
import uuid
from dao.dao import d

# Авторизация в сервисе GigaChat
chat = GigaChat(credentials="N2I2ODFmZDQtYjlhNS00ZGFkLTk1YjQtNDU5MjE5ODgyZDVlOmMwZjUxMTZlLTBmNjEtNGY3MC05MmQ3LTVjOWQzNzFiY2Q2ZA==", verify_ssl_certs=False)

messages = [
    SystemMessage(
        content="Ты - бот-сказочник. Рассказывай короткую сказку и предлагай слушателю придумать идею продолжения"
    )
]


def ask(prompt, username, uuid):
    # global chat, messages
    global chat
    # messages.append(HumanMessage(content=prompt))
    messages = [SystemMessage(content="Ты - бот-сказочник. Рассказывай короткую сказку и предлагай слушателю придумать идею продолжения")]
    for row in d.select("*", username, f"uuid = {uuid}"):
        # Предполагается, что у вас есть классы SystemMessage и HumanMessage
        # для создания объектов сообщений.
        if row[2] == 'SystemMessage':
            messages.append(SystemMessage(content=row[3]))
        elif row[2] == 'HumanMessage':
            messages.append(HumanMessage(content=row[3]))
        # else:
        #     messages.append(BaseMessage(content=row[3]))
    res = chat(messages)
    messages.append(res)
    return res.content


# Функция для генерации уникального идентификатора
def generate_unique_id():
    return str(uuid.uuid4())


# Функция для генерации названия с помощью ChatGPT
def generate_title_with_gpt(prompt):
   global chat
   messages = [
       SystemMessage(content="Ты придумываешь тезис к истории. Используй только данную тебе информацию, не додумывай от себя. Не пиши никаких вводных слов, только название без знаков препинания."),
       HumanMessage(content=prompt)
   ]
   res = chat(messages)
   return res.content

# # Пример использования
# story_id = generate_unique_id()
# story_prompt = "Царь и его дочери"
# story_title = generate_title_with_gpt(story_prompt)
#
# print(story_id)
# print(story_title)