from LIBRARY import *

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