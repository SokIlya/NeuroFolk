from flask import Flask, render_template, redirect, url_for, request, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from services.fusion_brain_service import Text2ImageAPI
from services.gigachat_service import ask
import json

from models.user import User, add_message, Message, db


api = Text2ImageAPI('https://api-key.fusionbrain.ai/', '41AAFF4A61197CFC06A0207D5A1D868A',
                    '9C4D73B733659059A2C901B092D9957C')

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'

db.init_app(app)
# with app.app_context():
#     db.create_all()





login_manager = LoginManager(app)
login_manager.login_view = 'login'

# class User(UserMixin, db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True, nullable=False)
#     password = db.Column(db.String(60), nullable=False)

# class Message(db.Model):
#     __tablename__ = "messages"
#     id = db.Column(db.Integer, primary_key=True)
#     sent = db.Column(db.Boolean)
#     content = db.Column(db.Text)
#     image = db.column(db.Text, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@login_required
@app.route('/reset_db')
def reset_db():
    if current_user.username == "admin":
        db.drop_all()
        db.create_all()
    else:
        flash('Это может сделать только администратор', 'error')
    return "Database has been reset."


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                login_user(user)
                flash('Login successful!', 'success')  # Example success message
                return redirect(url_for('chat'))
            else:
                flash('Incorrect password. Please try again.', 'error')
        else:
            flash('Username not found. Please register.', 'error')
    print(f'Flashed Messages: {get_flashed_messages()}')  # Debug statement
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        print(user)
        if not user:
            # hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('Registration successful!', 'success')  # Flash success message
            return redirect(url_for('chat'))
        else:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'POST':
        user_message = request.form['message']

        add_message(user_id=current_user.id, text=user_message, sent=True)


        ans = ask(current_user.id, user_message)
        base64_image = api.get_image(ans)


        add_message(user_id=current_user.id, text=ans, sent=False, image_base64=base64_image)



    user_messages = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp).all()


    return render_template('chat.html', messages=user_messages, chat_list=["1", "2"])
    # return render_template('chat.html', messages=[], chat_list=["1", "2"])


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

