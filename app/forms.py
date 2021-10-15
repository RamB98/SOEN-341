from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from app.models import User

class RegisterForm(FlaskForm):

    def validate_username(self, potential_username):
        user = User.query.filter_by(username=potential_username.data).first()
        if user:
            raise ValidationError('Username is already in use, please try another!')

    def validate_email(self, potential_email):
        em = User.query.filter_by(email=potential_email.data).first()
        if em:
            raise ValidationError('Email is already in use, please try another!')

    username = StringField(label='User Name:', validators=[Length(min=2, max=80)])
    email = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')