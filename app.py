from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import ChatForm, MessageForm, LoginForm, RegisterForm
from extensions import db
from services.gigachat_service import ask_gigachat, generate_system_prompt
from services.fusion_brain_service import txt_to_img
from io import BytesIO
from fpdf import FPDF, HTMLMixin
from models import User, Chat, Message
import base64
from PIL import Image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            new_user = User(username=form.username.data)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=form.remember.data)
            return redirect(url_for('index'))
        except Exception:
            pass

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    chat_id = request.args.get('chat_id', type=int)
    form = ChatForm()
    message_form = MessageForm()
    selected_chat = None
    messages = []

    if form.validate_on_submit():
        chat_name = form.name.data
        characters = ','.join(form.characters.data)
        main_idea = form.main_idea.data
        sys_prompt = generate_system_prompt(characters, main_idea)

        new_chat = Chat(name=chat_name, sys_prompt=sys_prompt, user_id=current_user.id)
        db.session.add(new_chat)
        db.session.commit()

        new_message = Message(content=chat_name, chat_id=new_chat.id, user_id=current_user.id,
                              sender_type="user")
        db.session.add(new_message)
        db.session.commit()

        try:
            answer_gigachat = str(ask_gigachat(new_chat.id, chat_name, sys_prompt))
        except Exception as e:
            answer_gigachat = str(e)
        answer_message = Message(content=answer_gigachat, chat_id=new_chat.id, user_id=current_user.id,
                                 sender_type="bot")
        db.session.add(answer_message)
        db.session.commit()

        base64img = txt_to_img.get_image(answer_gigachat)
        base64img_message = Message(content=base64img, is_img=True, chat_id=new_chat.id, user_id=current_user.id,
                                    sender_type="bot")
        db.session.add(base64img_message)
        db.session.commit()

        selected_chat = new_chat

        messages = Message.query.filter_by(chat_id=selected_chat.id).all()

    if chat_id:
        selected_chat = Chat.query.get_or_404(chat_id)
        if selected_chat.user_id != current_user.id:
            return redirect(url_for('index'))
        if message_form.validate_on_submit():
            new_message = Message(content=message_form.content.data, chat_id=selected_chat.id, user_id=current_user.id,
                                  sender_type="user")
            db.session.add(new_message)
            db.session.commit()
            try:
                answer_gigachat = str(ask_gigachat(selected_chat.id, message_form.content.data,
                                      selected_chat.sys_prompt))
            except Exception as e:
                answer_gigachat = str(e)
            answer_message = Message(content=answer_gigachat, chat_id=selected_chat.id, user_id=current_user.id,
                                     sender_type="bot")
            db.session.add(answer_message)
            db.session.commit()
            base64img = txt_to_img.get_image(answer_gigachat)
            base64img_message = Message(content=base64img, is_img=True, chat_id=selected_chat.id,
                                        user_id=current_user.id, sender_type="bot")
            db.session.add(base64img_message)
            db.session.commit()
            return redirect(url_for('index', chat_id=selected_chat.id))

        messages = Message.query.filter_by(chat_id=selected_chat.id).all()
    chats = Chat.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', form=form, chats=chats, selected_chat=selected_chat, message_form=message_form,
                           messages=messages)


@app.route('/delete_chat/<int:chat_id>', methods=['POST'])
@login_required
def delete_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if chat.user_id != current_user.id:
        return redirect(url_for('index'))
    db.session.delete(chat)
    db.session.commit()
    return redirect(url_for('index'))


class MyFPDF(FPDF, HTMLMixin):
    pass


@app.route('/download_pdf/<int:chat_id>', methods=['POST'])
@login_required
def download_pdf(chat_id):
    messages = Message.query.filter_by(chat_id=chat_id).all()

    chat = Chat.query.get_or_404(chat_id)
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)

    pdf.cell(200, 10, txt=f"Chat: {chat.name}", ln=True, align='C')

    user = User.query.get(messages[0].user_id)

    for message in messages:

        if user:
            if message.sender_type == "user":
                pdf.multi_cell(0, 10, txt=f"{user.username}: {message.content}", align='L')
            elif message.sender_type == "bot":
                if message.is_img:
                    try:
                        image_data = base64.b64decode(message.content)
                        image = Image.open(BytesIO(image_data))

                        if image.mode != 'RGB':
                            image = image.convert('RGB')

                        image_bytes = BytesIO()
                        image.save(image_bytes, format='PNG')
                        image_bytes.seek(0)

                        pdf.image(image_bytes, x=10, w=190)
                    except Exception as e:
                        print(f"Error decoding image for message ID {message.id}: {e}")
                        print(
                            f"Base64 content: {message.content[:30]}...")
                else:
                    pdf.multi_cell(0, 10, txt=f"Бот: {message.content}", align='L')
        else:
            pdf.multi_cell(0, 10, txt=f"Unknown User: {message.content}", align='L')

        pdf.ln(10)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return send_file(pdf_output, download_name=f"{chat.name}.pdf", as_attachment=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
