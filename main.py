from services.fusion_brain_service import Text2ImageAPI
import services.gigachat_service
import dao
import base64


def is_valid_password(password):
    special_characters = "~!@#$%^&*()-_=+[]{};:'\"\\|,.<>/?"
    return all([any([c.isupper() for c in password]),
                any([c.islower() for c in password]),
                any([c.isdigit() for c in password]),
                any([c in special_characters for c in password]),
                len(password) >= 8])


d = dao.dao.Dao("db.db")
d.create_table("users", "username TEXT, password TEXT")

command = input("reg - регистрация; login - вход: ")
while command not in ["reg", "login"]:
    print("Неизвестная команда\n")
    command = input("reg - регистрация; login - вход: ")


if command == "reg":
    username = input("Придумайте имя пользователя: ")
    while d.select("*", "users", f"username = '{username}'"):
        print("Пользователь с таким именем уже существует\n")
        username = input("Придумайте имя пользователя: ")

    password = input("Придумайте пароль: ")
    while not is_valid_password(password):
        print("Пароль должен содержать хотя бы:\n- 8 символов,\n- 1 строчную букву,\n- 1 заглавную букву,\n- 1 цифру,\n- 1 специальный символ (~!@#$%^&*()-_=+[]{};:'\"\\|,.<>/?)\n")
        password = input("Придумайте пароль: ")

    d.insert("users", "username, password", (username, password))
    print(f"\nПрофиль пользователя {username} создан!\n")
elif command == "login":
    username = input("Имя пользователя: ")
    while not d.select("*", "users", f"username = '{username}'"):
        print("Пользователя с таким именем не существет\n")
        username = input("Имя пользователя: ")

    password = input("Пароль: ")
    while password != d.select("password", "users", f"username = '{username}'")[0][0]:
        print("Неверный пароль\n")
        password = input("Пароль: ")

print(f"\nЗдравствуйте, {username}!\n")


api = Text2ImageAPI('https://api-key.fusionbrain.ai/', '41AAFF4A61197CFC06A0207D5A1D868A', '9C4D73B733659059A2C901B092D9957C')

print("Я расскажу тебе сказку, а потом вместе придумаем продолжение. С чего начнем?")

while True:
    user_input = input("User: ")
    ans = services.gigachat_service.ask(user_input)
    print(ans)

    img = api.get_image(ans)

    decoded_data = base64.b64decode(img)

    with open('output_image.jpg', 'wb') as img_file:
        img_file.write(decoded_data)