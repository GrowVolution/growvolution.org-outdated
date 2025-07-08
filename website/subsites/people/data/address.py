from website.data import DB
from sqlalchemy.ext.hybrid import hybrid_property


class Address(DB.Model):
    __tablename__ = 'people_addresses'

    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('people_accounts.id'), unique=True, nullable=False)
    street = DB.Column(DB.String(255), nullable=False)
    street_nr = DB.Column(DB.String(8), nullable=False)
    city = DB.Column(DB.String(100), nullable=False)
    state = DB.Column(DB.String(100))
    zip_code = DB.Column(DB.String(20), nullable=False)
    country = DB.Column(DB.String(100), default='Germany')

    user = DB.relationship('PeopleUser', backref='address', uselist=False, cascade='all')

    def __init__(self, user_id: int, street: str, street_nr: str, city: str, zip_code: str,
                 state: str =None, country: str ='Germany'):
        self.user_id = user_id
        self.street = street
        self.street_nr = street_nr
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country

    @hybrid_property
    def full_address(self) -> str:
        parts = [f"{self.street} {self.street_nr}", f"{self.zip_code} {self.city}", self.state, self.country]
        return ', '.join(part for part in parts if part)
