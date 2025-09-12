import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError

from moviedb.models.autenticacao import User

class Unique_Email(object):
    def __init__(self, message: str = 'Email ja registrado!'):
        if not message:
            message = 'Erro de integridade'
        self.message = message

    def __call__(self, form, field):
        if User.get_by_email(field.data):
            raise ValidationError(self.message)


class Senha_Complexa(object):
    def __init__(self,
                 message: str = None,
                 maiusculas: bool = True,
                 minusculas: bool = True,
                 simbolos: bool = True):
        self.message = "A senha não é complexa o bastante"
        self.maiusculas = maiusculas
        self.minusculas = minusculas
        self.simbolos = simbolos

    def __call__(self, form, field):
        valida = True
        if self.maiusculas:
            valida = valida and (re.search(r'[A-Z]', field.data) is not None)
        if self.minusculas:
            valida = valida and (re.search(r'[a-z]', field.data) is not None)



class RegistrationForm(FlaskForm):
    nome = StringField(
        label='Nome',
        validators=[
            InputRequired(message='Nome requerido!'),
            Length(max=60, message="O nome deve ter no máximo 60 caracteres.")
            ]
    )

    email = StringField(
        label='E-mail',
        validators=[
            InputRequired(message='E-mail requerido!'),
            Email(message='Informe um E-mail válido!'),
            Length(max=180, message="O e-mail deve no máximo 180 caracteres."),
            Unique_Email("Email já registrado!")
        ]
    )
    password = PasswordField(
        label='Senha',
        validators=[
            InputRequired(message='Senha requerido!'),
            Length(min=10, message="A senha deve ter 10 caracteres."),
            Senha_Complexa(maiusculas=True, minusculas=True, simbolos=True)
        ]
    )
    password2 = PasswordField(
        label="confirme a senha",
        validators=[
            InputRequired(message='Senha requerido!'),
            EqualTo('password', message='Senhas precisam ser iguais!')
        ]
    )
    submit = SubmitField('Criar uma conta')


class LoginForm(FlaskForm):
    email = StringField(
        label='E-mail',
        validators=[
            InputRequired(message='E-mail requerido!'),
            Email(message='Informe um E-mail válido!'),
            Length(max=180, message="O e-mail deve no máximo 180 caracteres.")
        ])
    password = PasswordField(
        label='Senha',
        validators=[
            InputRequired(message='Senha requerido!')
        ])

    remember_me = BooleanField(label='lembrar')

    submit = SubmitField('Logar')

