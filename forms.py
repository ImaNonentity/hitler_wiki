from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddPageForm(FlaskForm):
    start = StringField("Впиши сюда то, с чего начнется поиск", validators=[DataRequired()])
    goal = StringField("А где закончится поиск?", validators=[DataRequired()], default="Гитлер")
    submit = SubmitField("Подтвержаю начало операции")
