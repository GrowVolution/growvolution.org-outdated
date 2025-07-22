from ...utils.rendering import render
from ...data.roles import PrimaryRole, SecondaryRole
from ...data.user import UserType
from shared.data import DB
from markupsafe import Markup


def get_roles_html(can_manage: bool, user_spheres: list[UserType], primary: bool = True, search: str = ''):
    html = ''
    table = PrimaryRole if primary else SecondaryRole
    roles = DB.session.query(table).filter(
        table.name.ilike(f"%{search}%")
    ).limit(10).all()

    for role in roles:
        html += render('manage/role.html', role=role)


def process_context(user):
    can_manage = user.has_permissions(['manage_roles'])

    primary_roles = ""
    for role in PrimaryRole.query.all()[:10]:
        pass
