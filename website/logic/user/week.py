from website.rendering import render
from website.data import commit
from flask import request
from datetime import datetime


def handle_request(user):
    if not user.week_plan:
        return render('user/plan_week.html', user)

    today = datetime.now()
    current_day = ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'][today.weekday()]
    now = today.time()

    return render(
        'user/week.html',
        user=user,
        mode=user.week_plan_mode,
        week=user.active_week_tasks,
        current_day=current_day,
        now=now,
        reliability=None
    )


def _setup_task(user, data, mode):
    user.setup_week(
        mon=data.get('mo') or None,
        tue=data.get('di') or None,
        wed=data.get('mi') or None,
        thu=data.get('do') or None,
        fri=data.get('fr') or None,
        sat=data.get('sa') or None,
        sun=data.get('so') or None,
        mode=mode
    )


def setup_week(user):
    data = request.form
    mode = data.get('mode', 'simple')

    _setup_task(user, data, mode)
    user.add_xp(25 if mode == 'simple' else (50 if mode == 'medium' else 75))
    commit()

    return '', 200


def update_week(user):
    data = request.form
    mode = data.get('mode', 'simple')

    xp_update_data = user.week_xp_update_data(mode)
    _setup_task(user, data, mode)

    fn_map = {
        'add': user.add_xp,
        'remove': user.remove_xp
    }

    if xp_update_data:
        fn_map[xp_update_data[0]](xp_update_data[1])
    commit()


def edit_week(user):
    return render('user/plan_week.html', user)
