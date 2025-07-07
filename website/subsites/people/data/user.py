from website.data import DB, BCRYPT


class User(DB.Model):
    __tablename__ = 'people_accounts'

    id = DB.Column(DB.Integer, primary_key=True)
    first_name = DB.Column(DB.String(64), nullable=False)
    last_name = DB.Column(DB.String(64), nullable=False)
    email = DB.Column(DB.String(128), unique=True, nullable=False)
    phone = DB.Column(DB.String(32), unique=True)
    psw_hash = DB.Column(DB.String(256), nullable=False)

    temporary = DB.Column(DB.Boolean, default=True, nullable=False)

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
