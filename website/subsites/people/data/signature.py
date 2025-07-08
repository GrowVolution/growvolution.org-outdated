from website.data import DB


class Signature(DB.Model):
    __tablename__ = 'people_signatures'

    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    uid = DB.Column(DB.Integer, DB.ForeignKey('people_accounts.id'), nullable=False)
    timestamp = DB.Column(DB.DateTime, nullable=False, default=DB.func.now())
    token = DB.Column(DB.String(64), nullable=False, unique=True)

    user = DB.relationship('PeopleUser', backref='signatures')

    def __init__(self, user_id: int, token: str):
        self.uid = user_id
        self.token = token
