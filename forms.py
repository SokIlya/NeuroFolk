from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField, widgets, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтверждение пароля', validators=[DataRequired(), EqualTo('password')])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Зарегистрироваться')


class ChatForm(FlaskForm):
    name = StringField('Chat Name', validators=[DataRequired()])
    characters = SelectMultipleField('Characters', choices=[
        ('Волшебник', 'Волшебник'),
        ('Король', 'Король'),
        ('Королева', 'Королева'),
        ('Принц', 'Принц'),
        ('Принцесса', 'Принцесса'),
        ('Эльф', 'Эльф'),
        ('Гном', 'Гном'),
        ('Дракон', 'Дракон'),
        ('Леший', 'Леший'),
        ('Баба Яга', 'Баба Яга'),
        ('Кощей', 'Кощей'),
        ('Домовой', 'Домовой'),
        ('Рыцарь', 'Рыцарь'),
        ('Богатырь', 'Богатырь'),
        ('Змей Горыныч', 'Змей Горыныч'),
        ('Колобок', 'Колобок'),
        ('Русалка', 'Русалка'),
        ('Волк', 'Волк'),
        ('Собака', 'Собака'),
        ('Кот', 'Кот'),
        ('Великан', 'Великан'),
        ('Оборотень', 'Оборотень'),
        ('Белка', 'Белка'),
        ('Ворон', 'Ворон'),
        ('Фея', 'Фея'),
        ('Тролль', 'Тролль'),
        ('Осел', 'Осел'),
        ('Поросёнок', 'Поросёнок'),
        ('Буратино', 'Буратино'),
        ('Лебедь', 'Лебедь')
    ], option_widget=widgets.CheckboxInput(), widget=widgets.ListWidget(prefix_label=False))
    main_idea = TextAreaField('Main Idea')
    submit = SubmitField('Создать')


class MessageForm(FlaskForm):
    content = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Отправить')
