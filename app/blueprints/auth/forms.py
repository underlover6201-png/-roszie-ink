"""認證表單"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField(
        "帳號",
        validators=[DataRequired(message="請輸入帳號")],
    )
    password = PasswordField(
        "密碼",
        validators=[
            DataRequired(message="請輸入密碼"),
            Length(min=6, message="密碼至少 6 個字元"),
        ],
    )
    remember = BooleanField("記住我")
