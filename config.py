import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "4l3XS41o"  # Cambialo con uno più sicuro!
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'expma_db.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
