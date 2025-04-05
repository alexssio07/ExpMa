from app.database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password
        super().__init__()

    def set_hash_password(self, password):
        """Genera l'hash della password in ingresso e lo salva nel campo password_hash"""
        self.password_hash = generate_password_hash(password)

    def check_hash_password(self, password):
        """Controlla se la password in ingresso è corretta rispetto a quella salvata nel campo password_hash"""
        return check_password_hash(self.password_hash, password)

    def check_password(self, password):
        """Controlla se la password in ingresso è corretta rispetto a quella salvata nel campo password"""
        return self.password == password


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), unique=True, nullable=False)
    spesa = db.relationship("Spesa", backref="categoria", lazy=True)



class Spesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), nullable=False)
    descrizione = db.Column(db.String(150), nullable=False)
    tipologia_pagamento = db.Column(db.String(30), nullable=False)
    data_operazione = db.Column(db.DateTime, nullable=False)
    importo = db.Column(db.Float, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=True)


def get_user_by_id(user_id):
    """
    Funzione richiesta da Flask-Login per recuperare un utente dal database.

    Args:
        user_id (int): ID dell'utente

    Returns:
        user (User): Oggetto User con l'ID specificato
    """
    return User.query.get(int(user_id))
