from website.data import DB


class Signature(DB.Model):
    __tablename__ = 'people_signatures'

    id = DB.Column(DB.Integer, primary_key=True)
    uid = DB.Column(DB.Integer, DB.ForeignKey('people_accounts.id'), nullable=False)
    timestamp = DB.Column(DB.DateTime, nullable=False, default=DB.func.now())
