from shared.data import DB

PRIMARY_ROLES = DB.Table(
    'primary_roles',
    DB.Column('uid', DB.Integer, DB.ForeignKey('people_accounts.id'), primary_key=True),
    DB.Column('rid', DB.Integer, DB.ForeignKey('primary_role.id'), primary_key=True)
)

PRIMARY_ROLE_TYPES = DB.Table(
    'primary_role_types',
    DB.Column('tid', DB.Integer, DB.ForeignKey('people_account_type.id'), primary_key=True),
    DB.Column('rid', DB.Integer, DB.ForeignKey('primary_role.id'), primary_key=True)
)

SECONDARY_ROLES = DB.Table(
    'secondary_roles',
    DB.Column('uid', DB.Integer, DB.ForeignKey('people_accounts.id'), primary_key=True),
    DB.Column('rid', DB.Integer, DB.ForeignKey('secondary_role.id'), primary_key=True)
)

SECONDARY_ROLE_TYPES = DB.Table(
    'secondary_role_types',
    DB.Column('tid', DB.Integer, DB.ForeignKey('people_account_type.id'), primary_key=True),
    DB.Column('rid', DB.Integer, DB.ForeignKey('secondary_role.id'), primary_key=True)
)


class PrimaryRole(DB.Model):
    __tablename__ = 'primary_role'

    id = DB.Column(DB.Integer, primary_key=True)
    permission_id = DB.Column(DB.Integer, DB.ForeignKey('people_permissions.id'), nullable=False)
    name = DB.Column(DB.String(32), nullable=False, unique=True)

    users = DB.relationship('PeopleUser', secondary=PRIMARY_ROLES, backref='primary_roles', cascade='all')
    account_type = DB.relationship('UserType', secondary=PRIMARY_ROLE_TYPES, backref='primary_roles', cascade='all')
    permission = DB.relationship('PeoplePermission', back_populates='primary_roles', uselist=False, cascade='all')

    def __init__(self, name: str, permission_id: int):
        self.name = name
        self.permission_id = permission_id


class SecondaryRole(DB.Model):
    __tablename__ = 'secondary_role'

    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    permission_id = DB.Column(DB.Integer, DB.ForeignKey('people_permissions.id'), nullable=False)
    name = DB.Column(DB.String(32), nullable=False, unique=True)

    users = DB.relationship('PeopleUser', secondary=SECONDARY_ROLES, backref='secondary_roles', cascade='all')
    account_type = DB.relationship('UserType', secondary=SECONDARY_ROLE_TYPES, backref='secondary_roles', cascade='all')
    permission = DB.relationship('PeoplePermission', back_populates='secondary_roles', uselist=False, cascade='all')

    def __init__(self, name: str, permission_id: int):
        self.name = name
        self.permission_id = permission_id
