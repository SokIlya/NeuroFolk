from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class Chat(db.Model):
    __tablename__ = "chats"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to reference User
    text = db.Column(db.String, nullable=False)
    sent = db.Column(db.Boolean, nullable=False)
    image_base64 = db.Column(db.Text, nullable=True)  # Optional: for storing base64 image strings
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    chat = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Message %r>' % self.text


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    messages = db.relationship('Message', backref='user', lazy=True)  # Relationship to the Message model
    chats = db.relationship('Chat', secondary='user_chats', backref=db.backref('users', lazy=True))


    def __repr__(self):
        return '<User %r>' % self.username


def add_message(user_id, text, sent, image_base64=None):
    # Create a new message instance
    new_message = Message(user_id=user_id, text=text, sent=sent, image_base64=image_base64)

    # Add the new message to the database session
    db.session.add(new_message)

    # Commit the session to save the message to the database
    db.session.commit()

