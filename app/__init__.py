from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager
from app.models.models import User
from app.database import db
from app.routes.routes import routes_bp
from app.routes.auth_routes import auth_bp
from app.utils import utils_bp
from config import Config
from flask_migrate import Migrate


login_manager = LoginManager()


def create_app():
    """
    Crea l'oggetto app della web application e configura la base di dati SQLAlchemy.
    Registra i Blueprint per le rotte principali e per le rotte dell'API.

    Returns:
        app (Flask): Oggetto app della web application
    """
    app = Flask(__name__)  # Creo l'oggetto app della web application
    app.config.from_object(
        Config
    )  # Aggiungo il file di configurazione dell'applicazione al collegamento al database

    migrate = Migrate(app, db)
    with app.app_context():
        db.init_app(app)  # Inizializzo l'applicazione con SQLAlchemy
        db.create_all()  # Crea le tabelle nel database se non esistono

    login_manager.init_app(app)  # Inizializzo l'applicazione con Flask-Login
    login_manager.login_view = (
        "main.login"  # Redirect alla pagina di login se non autenticato
    )

    # Registro i Blueprint per le rotte principali e per le rotte dell'API
    app.register_blueprint(routes_bp)
    app.register_blueprint(utils_bp, url_prefix="/utils")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app


@login_manager.user_loader
def load_user(user_id):
    """Funzione per caricare un utente dato il suo ID"""
    return User.query.get(int(user_id))
