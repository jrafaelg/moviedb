import uuid

from sqlalchemy import Column, Uuid, String, Boolean

from moviedb import db

def normalizar_email(email: str) -> str:
    return email.lower()


class User(db.Model):
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
