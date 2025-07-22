from ...data.user import PeopleUser
from website.logic.auth import decoded_token
from flask import request


def get_user():
    decoded = decoded_token(request.cookies.get('token'))
    return PeopleUser.query.get(decoded['id']) if decoded else None
