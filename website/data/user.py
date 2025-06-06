from . import DB, BCRYPT, cloudinary, commit
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from typing import Optional
import random, string, os, pyotp


def randomize_username(username_raw: str) -> str:
    new_username = username_raw
    username_raw = username_raw.replace('_', '')

    for i in range(int(len(username_raw) / 7)):
        choice = random.choice(username_raw)
        new_char = random.choice(string.ascii_letters + string.digits)
        new_username = new_username.replace(choice, new_char)

    return new_username


def _get_fernet():
    key = os.getenv('TWOFA_KEY')
    return Fernet(key)


def _fernet_encrypted(data: bytes) -> str:
    return _get_fernet().encrypt(data).decode()


def _fernet_decrypted(data: bytes) -> str:
    return _get_fernet().decrypt(data).decode()


def _level_title(lvl: int) -> str:
    return {
        1: "Anfänger",
        2: "Aufgebrochen",
        3: "Wachsender",
        4: "Gestaltender",
        5: "Wandler"
    }.get(lvl, "Unbekannt")


class User(DB.Model):
    __tablename__ = 'user'
    id = DB.Column(DB.Integer, primary_key=True)

    google_id = DB.Column(DB.String(128), unique=True)
    apple_id = DB.Column(DB.String(128), unique=True)
    microsoft_id = DB.Column(DB.String(128), unique=True)
    psw_hash = DB.Column(DB.String(256))

    first_name = DB.Column(DB.String(48), nullable=False)
    last_name = DB.Column(DB.String(48), nullable=False)
    username = DB.Column(DB.String(32), unique=True, nullable=False)
    email = DB.Column(DB.String(128), unique=True, nullable=False)
    picture = DB.Column(DB.String(256), nullable=False, default='default')

    role = DB.Column(DB.String(8), nullable=False, default='user')

    birthdate = DB.Column(DB.Date)
    gender = DB.Column(DB.String(1))  # 'm', 'w', 'd'
    phone = DB.Column(DB.String(32))
    address = DB.Column(DB.String(255))  # format: street|number|postal_code|city

    xp = DB.Column(DB.Integer, nullable=False, default=0)
    level = DB.Column(DB.Integer, nullable=False, default=1)
    username_changed_at = DB.Column(DB.DateTime, default=datetime.utcnow)

    twofa_enabled = DB.Column(DB.Boolean, default=False)
    twofa_secret_enc = DB.Column(DB.String(172))
    twofa_recovery = DB.Column(DB.String(53))
    login_notify = DB.Column(DB.Boolean, default=True)

    comments = DB.relationship('Comment', back_populates='author', cascade='all, delete-orphan')
    replies = DB.relationship('Reply', back_populates='author', cascade='all, delete-orphan')

    def __init__(self,
                 first_name: str, last_name: str,
                 username: str, email: str, picture: str | None = None,
                 google_id: str | None = None, apple_id: str | None = None,
                 microsoft_id: str | None = None, password: str | None = None):

        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email

        self.google_id = google_id
        self.apple_id = apple_id
        self.microsoft_id = microsoft_id

        self.psw_hash = BCRYPT.generate_password_hash(password).decode() if password else None

        if picture:
            self.picture = picture

    @hybrid_property
    def oauth_provider(self) -> str | None:
        return 'google' if self.google_id else (
            'apple' if self.apple_id else (
                'microsoft' if self.microsoft_id else None
            )
        )

    def check_password(self, password: str) -> bool:
        return BCRYPT.check_password_hash(self.psw_hash, password)

    def set_password(self, password: str):
        self.psw_hash = BCRYPT.generate_password_hash(password)
        commit()

    def set_email(self, email: str):
        self.email = email
        commit()

    def set_picture(self, picture: str):
        self.picture = picture
        commit()

    def get_picture_url(self) -> str:
        pic = self.picture
        return pic if pic.startswith('http') else cloudinary.retrieve_asset_url(pic)

    def enable_2fa(self, secret: str) -> list[str]:
        codes = [''.join(random.choices(string.digits, k=8)) for _ in range(6)]

        self.twofa_enabled = True
        self.twofa_secret_enc = _fernet_encrypted(secret.encode())
        self.twofa_recovery = '|'.join(codes)
        commit()

        return codes

    def check_2fa_token(self, token: str) -> bool:
        if len(token) == 8 and self.twofa_recovery:
            codes = self.twofa_recovery.split('|')
            if token in codes:
                codes.remove(token)
                self.twofa_recovery = '|'.join(codes)
                return True
            return False

        try:
            if not self.twofa_secret_enc:
                return False
            secret = _fernet_decrypted(self.twofa_secret_enc.encode())
            return pyotp.TOTP(secret).verify(token)
        except (TypeError, AttributeError, InvalidToken):
            return False

    def disable_2fa(self):
        self.twofa_enabled = False
        self.twofa_secret_enc = None
        self.twofa_recovery = None
        commit()

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def can_change_username(self) -> bool:
        if not self.username_changed_at:
            return True
        delta = datetime.utcnow() - self.username_changed_at
        return delta.days >= 30

    def get_address_dict(self) -> Optional[dict]:
        if not self.address or "|" not in self.address:
            return None
        parts = self.address.split("|")
        if len(parts) != 4:
            return None
        return {
            "street": parts[0],
            "number": parts[1],
            "postal": parts[2],
            "city": parts[3]
        }

    def get_address_str(self) -> str:
        a = self.get_address_dict()
        return f"{a['street']} {a['number']}, {a['postal']} {a['city']}" if a else "Keine Angabe"

    def set_address(self, street: str, number: str, postal: str, city: str):
        self.address = f"{street}|{number}|{postal}|{city}"
        commit()

    def get_level_status(self) -> str:
        return _level_title(self.level)

    def get_next_level_status(self) -> str:
        return _level_title(self.level + 1)
