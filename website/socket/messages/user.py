from . import register_message
from .. import emit


@register_message('score_update', ['user/dashboard', 'user/profile'])
def score_update(user, data):
    data = {
        'score': user.score,
        'level': user.level,
        'level_icon': user.level_icon,
        'level_status': user.level_status,
        'next_level_status': user.next_level_status
    }
    emit('score_update', data, user)
