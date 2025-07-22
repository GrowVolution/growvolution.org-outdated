from .. import cloudinary
from shared.data import DB, BCRYPT
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime


class UserBase:
    google_id = DB.Column(DB.String(128), unique=True)
    apple_id = DB.Column(DB.String(128), unique=True)
    microsoft_id = DB.Column(DB.String(128), unique=True)
    psw_hash = DB.Column(DB.String(256))

    first_name = DB.Column(DB.String(48), nullable=False)
    last_name = DB.Column(DB.String(48), nullable=False)
    username = DB.Column(DB.String(32), unique=True, nullable=False)
    picture = DB.Column(DB.String(256), nullable=False, default='default')

    email = DB.Column(DB.String(128), unique=True, nullable=False)
    email_change_code = DB.Column(DB.String(6))

    role = DB.Column(DB.String(8), nullable=False, default='user')

    username_changed_at = DB.Column(DB.DateTime)
    onboarding_shown = DB.Column(DB.Boolean, default=False)

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

    @hybrid_property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @hybrid_property
    def picture_url(self) -> str:
        pic = self.picture
        return pic if pic.startswith('http') else cloudinary.retrieve_asset_url(pic)

    @hybrid_property
    def can_change_username(self) -> bool:
        if not self.username_changed_at:
            return True
        delta = datetime.now() - self.username_changed_at
        return delta.days >= 30

    def check_password(self, password: str) -> bool:
        return BCRYPT.check_password_hash(self.psw_hash, password)

    def set_password(self, password: str):
        self.psw_hash = BCRYPT.generate_password_hash(password)

    def set_username(self, username: str):
        self.username = username
        self.username_changed_at = datetime.now()
