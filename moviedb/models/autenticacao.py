import uuid

from flask import current_app
from flask_login import UserMixin
from sqlalchemy import Column, Uuid, String, Boolean, select, func, DateTime
from werkzeug.security import generate_password_hash, check_password_hash

from moviedb.models.mixins import BasicRepositoryMixin
from moviedb import db

def normalizar_email(email: str) -> str:
    return email.lower()


class User(db.Model, BasicRepositoryMixin, UserMixin):
    __tablename__ = 'usuarios'

    id = Column(Uuid(as_uuid=True) , primary_key=True, default=uuid.uuid4)
    nome = Column(String(60), nullable=False)
    email_normalizado = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    data_cadastro = Column(DateTime, server_default=func.now(), nullable=False)

    @property
    def email(self):
        return self.email_normalizado

    @email.setter
    def email(self, value):
        self.email_normalizado = normalizar_email(value)

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def is_active(self):
        return self.ativo

    def get_id(self):
        return f"{str(self.id)}|{self.password[-15:]}"

    @classmethod
    def get_by_email(cls, email):
        return db.session.execute(select(cls).where(cls.email_normalizado == normalizar_email(email))).scalar_one_or_none()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def send_email(self,
                   subject: str,
                   body: str,) -> bool:
        """
        Envia um e-mail para o usuário utilizando o serviço Postmark.

        Args:
            subject (str): Assunto do e-mail.
            body (str): Corpo do e-mail em texto simples.

        Returns:
            True se conseguir enviar o e-mail, False caso contrário.
        """
        from postmarker.core import PostmarkClient
        postmark = PostmarkClient(server_token=current_app.config["SEVER_TOKEN"])
        conteudo = postmark.emails.Email(
            From=
        )