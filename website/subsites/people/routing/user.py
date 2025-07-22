from . import require_manage_permissions
from ..logic import manage as managing
from flask import Blueprint

user = Blueprint('user', __name__)


@user.route('/manage')
@require_manage_permissions(False, True)
def manage(usr):
    return managing.handle_request(usr)
