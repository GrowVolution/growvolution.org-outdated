from . import DATABASE
from ..utils import UTILS
from shared.data import DB

from sqlalchemy.ext.hybrid import hybrid_property

GROUPS = DB.Table(
    'env_groups',
    DB.Column('var', DB.Integer, DB.ForeignKey('env.id'), primary_key=True),
    DB.Column('group', DB.String(32), DB.ForeignKey('env_group.name'), primary_key=True)
)


@DATABASE.register('env')
class Environment(DB.Model):
    __tablename__ = 'env'

    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    key = DB.Column(DB.String(32), nullable=False)
    value_enc = DB.Column(DB.Text, nullable=False)

    def __init__(self, key: str, value: str):
        self.key = key
        self.update_value(value)

    @hybrid_property
    def value(self):
        decrypted = UTILS.resolve('decrypt')
        return decrypted(self.value_enc.encode())

    def update_value(self, new_value: str):
        encrypted = UTILS.resolve('encrypt')
        self.value_enc = encrypted(new_value.encode())


@DATABASE.register('env_group')
class EnvironmentGroup(DB.Model):
    __tablename__ = 'env_group'

    name = DB.Column(DB.String(32), nullable=False, unique=True, primary_key=True)
    protected = DB.Column(DB.Boolean, nullable=False, default=False)
    production = DB.Column(DB.Boolean, nullable=False, default=False)

    vars = DB.relationship('Environment', secondary=GROUPS, backref='groups', cascade='all')

    def __init__(self, name: str):
        self.name = name

    def add_var(self, var: Environment):
        self.vars.append(var)

    def pop_var(self, var: Environment):
        self.vars.remove(var)

    def set_protected(self, protected: bool):
        self.protected = protected

    def set_production(self, production: bool):
        self.production = production
        if production:
            self.protected = True
            prev = self.query.filter_by(production=True).first()
            if prev:
                prev.set_production(False)
