import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError

from moviedb.models.autenticacao import User

class UniqueEmail(object):
    def __init__(self, message: str = 'Email ja registrado!'):
        if not message:
            message = 'Erro de integridade'
        self.message = message

    def __call__(self, form, field):
        if User.get_by_email(field.data):
            raise ValidationError(self.message)


class SenhaComplexa(object):
    """
    Validador WTForms para garantir que a senha informada atende aos requisitos de complexidade
    definidos.

    Os requisitos são definidos pelas seguintes chaves inteiras e booleanas no
    dicionário de configuração da aplicação:

    - PASSWORD_MIN: 8
    - PASSWORD_MINUSCULA: false
    - PASSWORD_NUMERO: false
    - PASSWORD_SIMBOLO: false
    - PASSWORD_MAIUSCULA: false
    """

    def __init__(self):
        pass

    def __call__(self, form, field):
        """
        Realiza a validação da senha conforme os requisitos definidos.

        Args:
            form: O formulário sendo validado.
            field: O campo de senha a ser verificado.

        Raises:
            ValidationError: Se a senha não atender aos requisitos de complexidade.
        """
        from flask import current_app
        import re
        from collections import namedtuple

        Teste = namedtuple('Teste', ['config', 'mensagem', 're'])

        lista_de_testes = [
            Teste('PASSWORD_MAIUSCULA', "letras maiúsculas", r'[A-Z]'),
            Teste('PASSWORD_MINUSCULA', "letras minúsculas", r'[a-z]'),
            Teste('PASSWORD_NUMERO', "números", r'\d'),
            Teste('PASSWORD_SIMBOLO', "símbolos especiais", r'\W')
        ]

        min_caracteres = current_app.config.get('PASSWORD_MIN', 8)
        senha_valida = (len(field.data) >= min_caracteres)
        mensagens = [f"A sua senha precisa ter pelo menos {min_caracteres} caracteres"]

        for teste in lista_de_testes:
            if current_app.config.get(teste.config, False):
                senha_valida = senha_valida and (re.search(teste.re, field.data) is not None)
                mensagens.append(teste.mensagem)

        mensagem = ', '.join(mensagens)
        pos = mensagem.rfind(', ')

        if pos > -1:
            mensagem = mensagem[:pos] + ' e ' + mensagem[pos + 2:]

        if not senha_valida:
            raise ValidationError(mensagem)
        return



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
            UniqueEmail("Email já registrado!")
        ]
    )

    password = PasswordField(
        label='Senha',
        validators=[
            InputRequired(message='Senha requerido!'),
            Length(min=10, message="A senha deve ter 10 caracteres."),
            SenhaComplexa(maiusculas=True, minusculas=True, simbolos=True)
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

