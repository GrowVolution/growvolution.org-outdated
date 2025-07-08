from website.data import DB


class PeoplePermission(DB.Model):
    __tablename__ = 'people_permissions'

    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    name = DB.Column(DB.String(32), nullable=False, unique=True)

    # Management
    administrative = DB.Column(DB.Boolean, default=False)

    view_users = DB.Column(DB.Boolean, default=False)
    manage_users = DB.Column(DB.Boolean, default=False)

    view_roles = DB.Column(DB.Boolean, default=False)
    manage_roles = DB.Column(DB.Boolean, default=False)

    view_permissions = DB.Column(DB.Boolean, default=False)
    manage_permissions = DB.Column(DB.Boolean, default=False)

    view_reports = DB.Column(DB.Boolean, default=False)
    manage_reports = DB.Column(DB.Boolean, default=False)
    moderate_content = DB.Column(DB.Boolean, default=False)

    create_meetings = DB.Column(DB.Boolean, default=False)
    view_protocols = DB.Column(DB.Boolean, default=False)
    export_protocols = DB.Column(DB.Boolean, default=False)
    initiate_vote = DB.Column(DB.Boolean, default=False)

    view_transactions = DB.Column(DB.Boolean, default=False)
    manage_transactions = DB.Column(DB.Boolean, default=False)
    export_finance_data = DB.Column(DB.Boolean, default=False)

    view_applications = DB.Column(DB.Boolean, default=False)
    manage_applications = DB.Column(DB.Boolean, default=False)

    view_requests = DB.Column(DB.Boolean, default=False)
    manage_requests = DB.Column(DB.Boolean, default=False)

    send_notifications = DB.Column(DB.Boolean, default=False)

    # People Areas
    association_area = DB.Column(DB.Boolean, default=False)
    company_area = DB.Column(DB.Boolean, default=False)
    bank_area = DB.Column(DB.Boolean, default=False)
    external_area = DB.Column(DB.Boolean, default=False)

    # Relations
    primary_roles = DB.relationship('PrimaryRole', back_populates='permission')
    secondary_roles = DB.relationship('SecondaryRole', back_populates='permission')

    def __init__(self, name: str):
        self.name = name

    def is_allowed(self, permission: str) -> bool:
        if self.administrative:
            return True
        return getattr(self, permission, False)
