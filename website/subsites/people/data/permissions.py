from shared.data import DB
from sqlalchemy.ext.hybrid import hybrid_property

MANAGE_PERMS = [
    'administrative',
    'view_users', 'manage_users',
    'view_roles', 'manage_roles',
    'view_permissions', 'manage_permissions',
    'view_reports', 'manage_reports', 'moderate_content',
    'view_transactions', 'manage_transactions', 'export_finance_data',
    'create_meetings', 'view_protocols', 'export_protocols', 'initiate_vote',
    'view_applications', 'manage_applications',
    'view_requests', 'manage_requests',
    'send_notifications',
]

AREA_PERMS = [
    'association_area', 'company_area', 'bank_area', 'external_area'
]

ALL_PERMS = MANAGE_PERMS + AREA_PERMS


class PeoplePermission(DB.Model):
    __tablename__ = 'people_permissions'

    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    name = DB.Column(DB.String(32), nullable=False, unique=True)

    for perm in ALL_PERMS:
        vars()[perm] = DB.Column(DB.Boolean, default=False)

    primary_roles = DB.relationship('PrimaryRole', back_populates='permission')
    secondary_roles = DB.relationship('SecondaryRole', back_populates='permission')

    def __init__(self, name: str):
        self.name = name

    @hybrid_property
    def can_manage(self):
        return any(getattr(self, p, False) for p in MANAGE_PERMS)

    def is_allowed(self, permission: str) -> bool:
        if self.administrative:
            return True
        return getattr(self, permission, False)
