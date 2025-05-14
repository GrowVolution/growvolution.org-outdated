from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

DB = SQLAlchemy()
BCRYPT = Bcrypt()


def commit():
    DB.session.commit()


def add_model(model: DB.Model):
    DB.session.add(model)
    commit()


def delete_model(model: DB.Model):
    DB.session.delete(model)
    commit()