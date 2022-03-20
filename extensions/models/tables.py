from json import load
from extensions.database import db
from extensions.auth import encrypt
from werkzeug.security import check_password_hash
from flask import request, url_for
from requests import post
import os
from dotenv import load_dotenv


class UserModel(db.Model):
    __tablename__ = "clientes"
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(16), nullable=False)

    def __init__(self, name: str, email: str, password: str, active: bool) -> None:
        self.name = name
        self.email = email
        self.password = encrypt(password)
        self.active = active

    def json(self):
        return {"user_id": self.id, "name": self.name, "active": self.active}

    # Database queries
    @classmethod
    def find_user(cls, id):
        user = cls.query.filter_by(id=id).first()
        if user:
            return user
        return None

    @classmethod
    def find_email(cls, email):
        e_mail = cls.query.filter_by(email=email).first()
        if e_mail:
            return e_mail
        return None

    def check_pwd(self, req_pwd):
        return check_password_hash(self.password, req_pwd)

    def create_db():
        db.create_all()

    def save_user(self):
        db.session.add(self)
        db.session.commit()

    def delete_user(self):
        db.session.delete(self)
        db.session.commit()

    def send_confirmation_email(self):
        load_dotenv()
        FROM_TITLE = "No-Reply"
        FROM_EMAIL = "no-reply@restapi.com"
        link = request.url_root[:-1] + url_for("api.userconfirm", id=self.id)

        return post(
            f"https://api.mailgun.net/v3/{os.getenv('MAILGUN_DOMAIN')}/messages",
            auth=("api", os.getenv("MAILGUN_API_KEY")),
            data={
                "from": f"{FROM_TITLE} <{FROM_EMAIL}>",
                "to": self.email,
                "subject": "Confirmação de cadastro",
                "text": f"Confirme seu cadastro clicando no link a seguir: {link}",
                "html": f'<html><h1>"Confirme seu cadastro clicando no link a seguir: <a href="{link}">CONFIRMAR EMAIL</a></h1></html>"',
            },
        )
