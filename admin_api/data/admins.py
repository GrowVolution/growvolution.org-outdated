from . import DATABASE
from shared.data import DB
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from datetime import datetime, UTC
import secrets, json


@DATABASE.register('admin')
class Admin(DB.Model):
    __tablename__ = 'admins'

    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    name = DB.Column(DB.String(32), nullable=False, unique=True)
    email = DB.Column(DB.String(128), nullable=False, unique=True)
    pub_key = DB.Column(DB.LargeBinary, nullable=False, unique=True)
    key_timestamp = DB.Column(DB.DateTime, nullable=False)

    def __init__(self, name: str, email: str, pub_key: bytes):
        self.name = name
        self.email = email
        self.pub_key = pub_key
        self.key_timestamp = datetime.now(UTC)

    def verify_signature(self, data: dict, signature_hex: str) -> bool:
        public_key = serialization.load_pem_public_key(self.pub_key)
        signature = bytes.fromhex(signature_hex)

        payload = json.dumps(data, separators=(',', ':'), sort_keys=True).encode()
        try:
            public_key.verify(
                signature,
                payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False


@DATABASE.register('token')
class AdminToken(DB.Model):
    __tablename__ = 'admin_tokens'

    token = DB.Column(DB.String(64), nullable=False, unique=True, primary_key=True)
    email = DB.Column(DB.String(128), nullable=False)

    def __init__(self, email: str):
        self.token = secrets.token_hex(32)
        self.email = email
