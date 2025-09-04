from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    nome = StringField(
        label='Nome',
        validators=[
            InputRequired(message='Nome requerido!'),
            Length(max=60, message="O nome deve ter no máximo 60 caracteres.")
            ])
    email = StringField(
        label='E-mail',
        validators=[InputRequired(message='E-mail requerido!'),
                    Email(message='Informe um E-mail válido!'),
                    Length(max=180, message="O e-mail deve no máximo 180 caracteres.")])
    password = PasswordField(
        label='Senha',
        validators=[InputRequired(message='Senha requerido!'),]
    )
    password2 = PasswordField(
        label="confirme a senha",
        validators=[InputRequired(message='Senha requerido!'),
                    EqualTo('password', message='Senha requerido!')]
    )
    submit = SubmitField('Criar uma conta')
