from . import DATABASE
from shared.data import DB
from admin_api.utils import fernet_encrypted, fernet_decrypted
from sqlalchemy.ext.hybrid import hybrid_property


@DATABASE.register('env')
class Environment(DB.Model):
    __tablename__ = 'env'

    key = DB.Column(DB.String(32), nullable=False, unique=True, primary_key=True)
    value_enc = DB.Column(DB.Text, nullable=False)

    def __init__(self, key: str, value: str):
        self.key = key
        self.update_value(value)

    @hybrid_property
    def value(self):
        return fernet_decrypted(self.value_enc.encode())

    def update_value(self, new_value: str):
        self.value_enc = fernet_encrypted(new_value.encode())
