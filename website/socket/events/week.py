from . import register_event, require_user
from .. import emit
from website.data import commit
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
        if raw == 'restday':
            week_data[day] = 'restday'
        elif not raw:
            week_data[day] = None
        else:
            try:
                week_data[day] = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                week_data[day] = raw

    emit('load_weekplan', {'mode': mode, 'week': week_data})


@register_event('week_task_done')
@require_user(True)
def week_task_done(user, task_id):
    user.set_task_done(task_id)
    commit()
    emit('reliability_score', user.week_reliability_score)
