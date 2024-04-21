from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from dao.dao import d
from services.fusion_brain_service import Text2ImageAPI
from services.gigachat_service import ask


app = Flask(__name__)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

api = Text2ImageAPI('https://api-key.fusionbrain.ai/', '41AAFF4A61197CFC06A0207D5A1D868A',
                    '9C4D73B733659059A2C901B092D9957C')

messages = []
username = ""
uuid = "13232323"


def is_valid_password(password):
    special_characters = "~!@#$%^&*()-_=+[]{};:'\"\\|,.<>/?"
    return all([any([c.isupper() for c in password]),
                any([c.islower() for c in password]),
                any([c.isdigit() for c in password]),
                any([c in special_characters for c in password]),
                len(password) >= 8])


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global username
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username)
        print(password)

        if not d.select("*", "users", f"username = '{username}'"):
            print("Пользователя с таким именем не существет\n")
        elif password != d.select("password", "users", f"username = '{username}'")[0][0]:
            print("Неверный пароль\n")
        else:
            return redirect(url_for('chat'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    global username
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if d.select("*", "users", f"username = '{username}'"):
            print("Пользователь с таким именем уже существует\n")
        else:
            if 0:
                pass
            # if not is_valid_password(password):
            #     print("Пароль должен содержать хотя бы:\n- 8 символов,\n- 1 строчную букву,\n- 1 заглавную букву,\n- 1 цифру,\n- 1 специальный символ (~!@#$%^&*()-_=+[]{};:'\"\\|,.<>/?)\n")
            else:
                d.insert("users", "username, password", (username, password))
                d.create_table(username, "story_name TEXT, uuid TEXT, message_type TEXT, message TEXT")
                print(f"\nПрофиль пользователя {username} создан!\n")

        print(username)
        print(password)
        return redirect(url_for('chat'))
    return render_template('register.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    # global messages, username
    try:
        global username, uuid, messages
        if request.method == 'POST':
            for i, row in enumerate(d.select("*", username, f"uuid = {uuid}"), start=1):
                # Предполагается, что у вас есть классы SystemMessage и HumanMessage
                # для создания объектов сообщений.
                if i % 2 == 1:
                    messages.append({'text': row[3], 'sent': True})
                else:
                    messages.append({'text': row[3], 'sent': False})
            print(messages)
            user_message = request.form['message']
            print(user_message)
            ans = ask(user_message, username, uuid)
            base64_image = api.get_image(ans)
            print(ans)
            messages.append({'text': user_message, 'sent': True})
            messages.append({'text': ans, 'sent': False, 'image_base64': base64_image})
        chat_list = set([el[0] for el in d.select("story_name", username)])
        return render_template('chat.html', messages=messages, chat_list=chat_list)
    except Exception as e:
        print(e)
        return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
