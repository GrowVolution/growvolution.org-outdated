from . import DB, delete_model
from website import APP
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta
import secrets


class DevToken(DB.Model):
    __tablename__ = 'dev_token'
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(32), unique=True, nullable=False)
    token = DB.Column(DB.String(64), unique=True, nullable=False)
    timestamp = DB.Column(DB.DateTime, nullable=False, server_default=DB.func.now())
    days_valid = DB.Column(DB.Integer, nullable=False)

    def __init__(self, name: str, days_valid: int):
        self.name = name
        self.days_valid = days_valid
        self.set_token()

    @hybrid_property
    def valid(self) -> bool:
        delta_valid = timedelta(days=self.days_valid)
        return datetime.now() - self.timestamp <= delta_valid

    def set_token(self):
        if not self.token:
            self.token = secrets.token_hex(32)


def update_database():
    with APP.app_context():
        for token in DevToken.query.all():
            if not token.valid:
                delete_model(token)
