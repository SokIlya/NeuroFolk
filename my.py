from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import uuid
import base64

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    messages = db.relationship('Message', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    img_base64 = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username is None or password is None:
        return make_response('Missing username or password', 400)

    if User.query.filter_by(username=username).first() is not None:
        return make_response('User already exists', 400)

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'username': user.username}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user is None or not user.check_password(password):
        return make_response('Invalid username or password', 401)

    return jsonify({'login': 'success'}), 200

@app.route('/message', methods=['POST'])
def post_message():
    data = request.get_json()
    user_id = data.get('user_id')
    content = data.get('content')
    img_data = data.get('img_base64')

    user = User.query.get(user_id)
    if user is None:
        return make_response('User not found', 404)

    message = Message(content=content, img_base64=img_data, author=user)
    db.session.add(message)
    db.session.commit()

    return jsonify({'message': 'Message posted successfully'}), 201

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)