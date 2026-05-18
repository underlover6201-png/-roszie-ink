"""認證表單"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(message="請輸入 Email"), Email(message="Email 格式不正確")],
    )
    password = PasswordField(
        "密碼",
        validators=[
            DataRequired(message="請輸入密碼"),
            Length(min=6, message="密碼至少 6 個字元"),
        ],
    )
    remember = BooleanField("記住我")
