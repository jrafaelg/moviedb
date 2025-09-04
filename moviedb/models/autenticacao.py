import uuid

from flask_login import UserMixin
from sqlalchemy import Column, Uuid, String, Boolean
from werkzeug.security import generate_password_hash

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