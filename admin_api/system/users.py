from . import SYSTEM
from ..data.admins import AdminToken
from ..utils.mail_service import token_mail
from shared.data import add_model


@SYSTEM.register('send_token')
def send_token(data):
    email = data.get('email')
    name = data.get('name')

    if not (email and name):
        return False

    token_obj = AdminToken(email)
    add_model(token_obj)

    token_mail(email, name, token_obj.token)
    return True
