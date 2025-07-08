from website.data import DB, BCRYPT, add_model, commit
from website.utils import fernet_encrypted, fernet_decrypted
from cryptography.fernet import InvalidToken
import random, string, pyotp

USER_TYPES = DB.Table(
    'people_account_types',
    DB.Column('uid', DB.Integer, DB.ForeignKey('people_accounts.id'), primary_key=True),
    DB.Column('tid', DB.Integer, DB.ForeignKey('people_account_type.id'), primary_key=True)
)


class PeopleUser(DB.Model):
    __tablename__ = 'people_accounts'

    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    first_name = DB.Column(DB.String(64), nullable=False)
    last_name = DB.Column(DB.String(64), nullable=False)
    email = DB.Column(DB.String(128), unique=True, nullable=False)
    phone = DB.Column(DB.String(32), unique=True)
    psw_hash = DB.Column(DB.String(256), nullable=False)

    twofa_set = DB.Column(DB.Boolean, default=False)
    twofa_secret_enc = DB.Column(DB.String(172))
    twofa_recovery = DB.Column(DB.String(53))
    twofa_for_login = DB.Column(DB.Boolean, default=False)

    temporary = DB.Column(DB.Boolean, default=True, nullable=False)

    account_types = DB.relationship('UserType', secondary=USER_TYPES, backref='users', cascade='all')

    def __init__(self, first_name: str, last_name: str, email: str, password: str, phone: str | None = None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone if phone and phone.strip() else None
        self.psw_hash = BCRYPT.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return BCRYPT.check_password_hash(self.psw_hash, password)

    def verify(self):
        self.temporary = False

    def has_permissions(self, permissions: list[str], strict: bool = False) -> bool:
        allowed = {}
        for role in self.primary_roles + self.secondary_roles:
            for permission in permissions:
                if allowed.get(permission, False):
                    continue
                elif role.permission.is_allowed(permission):
                    allowed[permission] = True
                else:
                    allowed[permission] = False

        for permission in permissions:
            if strict and not allowed.get(permission, False):
                return False
            elif not strict and allowed.get(permission, False):
                return True

        return strict

    def set_2fa(self, secret: str) -> list[str]:
        codes = [''.join(random.choices(string.digits, k=8)) for _ in range(6)]

        self.twofa_set = True
        self.twofa_secret_enc = fernet_encrypted(secret.encode())
        self.twofa_recovery = '|'.join(codes)

        return codes

    def check_2fa_token(self, token: str, verify_signature: bool = False) -> bool:
        if not verify_signature and len(token) == 8 and self.twofa_recovery:
            codes = self.twofa_recovery.split('|')
            if token in codes:
                codes.remove(token)
                self.twofa_recovery = '|'.join(codes)
                commit()
                return True
            return False

        try:
            if not self.twofa_secret_enc:
                return False
            secret = fernet_decrypted(self.twofa_secret_enc.encode())
            return pyotp.TOTP(secret).verify(token)
        except (TypeError, AttributeError, InvalidToken):
            return False

    def unset_2fa(self):
        self.twofa_set = False
        self.twofa_secret_enc = None
        self.twofa_recovery = None
        self.twofa_for_login = False

    def enable_2fa(self):
        if not self.twofa_set:
            return
        self.twofa_for_login = True

    def disable_2fa(self):
        self.twofa_for_login = False


class UserType(DB.Model):
    __tablename__ = 'people_account_type'

    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    name = DB.Column(DB.String(32), nullable=False)

    def __init__(self, name: str):
        self.name = name


def init_types():
    default_types = [
        'association',
        'company',
        'bank',
        'external'
    ]

    for t in default_types:
        user_type = UserType.query.filter_by(name=t).first()
        if user_type:
            continue

        user_type = UserType(t)
        add_model(user_type)
