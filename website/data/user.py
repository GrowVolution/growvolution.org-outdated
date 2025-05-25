from . import DB, BCRYPT, cloudinary, commit
import random, string


def randomize_username(username_raw: str) -> str:
    new_username = username_raw
    username_raw = username_raw.replace('_', '')

    for i in range(int(len(username_raw) / 7)):
        choice = random.choice(username_raw)
        new_char = random.choice(string.ascii_letters + string.digits)
        new_username = new_username.replace(choice, new_char)

    return new_username


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

    def check_password(self, password: str) -> bool:
        return BCRYPT.check_password_hash(self.psw_hash, password)

    def set_password(self, password: str):
        self.psw_hash = BCRYPT.generate_password_hash(password)
        commit()

    def set_picture(self, picture: str):
        self.picture = picture
        commit()

    def get_picture_url(self) -> str:
        pic = self.picture
        return pic if pic.startswith('http') else cloudinary.retrieve_asset_url(pic, cloudinary.PROFILE_PIC_FOLDER)