from database import db
from flask_login import UserMixin
from datetime import datetime
import hashlib

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    senha_hash = db.Column(db.String(256), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, nome, senha_hash, email=None):
        self.nome = nome
        self.senha_hash = senha_hash
        self.email = email

    def get_id(self):
        """Retorna o ID do usuário, necessário para Flask-Login."""
        return str(self.id)

    def __repr__(self):
        return f'<Usuario {self.nome}>'