from . import register_event, require_user
from .. import emit
from debugger import log
import json

@register_event('request_weekplan')
@require_user(True)
def handle_week_request(user):
    week_data = {}
    mode = user.week_plan_mode or 'simple'

    for day, attr in zip(
            ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'],
            ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    ):
        raw = getattr(user, attr)
        log('debug', raw)
        if raw == 'restday':
            week_data[day] = 'restday'
        elif not raw:
            week_data[day] = None
        else:
            try:
                week_data[day] = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                week_data[day] = None

    emit('load_weekplan', {'mode': mode, 'week': week_data})
