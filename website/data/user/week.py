from .. import DB
from ..helpers import parse_time_str
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta
import json

XP_MAP = {
    'simple': 25,
    'medium': 50,
    'free': 75
}


class UserWeek:
    week_plan = DB.Column(DB.Boolean, default=False)

    monday = DB.Column(DB.Text)
    tuesday = DB.Column(DB.Text)
    wednesday = DB.Column(DB.Text)
    thursday = DB.Column(DB.Text)
    friday = DB.Column(DB.Text)
    saturday = DB.Column(DB.Text)
    sunday = DB.Column(DB.Text)

    week_plan_mode = DB.Column(DB.String(16))

    @hybrid_property
    def active_week_tasks(self) -> dict[str, str | list[dict]]:
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())

        data = {}
        for day_code, attr in zip(
                ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'],
                ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        ):
            raw = getattr(self, attr)
            if raw == 'restday' or not raw:
                data[day_code] = 'restday' if raw == 'restday' else None
                continue

            try:
                tasks = json.loads(raw)
            except json.JSONDecodeError:
                data[day_code] = None
                continue

            filtered = []
            for task in tasks:
                try:
                    start_date = datetime.strptime(task.get('start_date', ''), '%Y-%m-%d').date()
                    frequency = task.get('frequency', 'weekly')
                    multi = task.get('multi') is True or task.get('multi') == '1'
                    weekdays = task.get('weekdays') or []
                except (ValueError, TypeError):
                    continue

                weekday_index = ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'].index(day_code)
                day_date = monday + timedelta(days=weekday_index)

                diff = (day_date - start_date).days
                if diff < 0:
                    continue

                freq_map = {
                    'weekly': 7,
                    'biweekly': 14,
                    'triweekly': 21,
                    'fourweekly': 28
                }
                interval = freq_map.get(frequency, 7)
                if diff % interval != 0:
                    continue

                if multi and day_code not in weekdays:
                    continue

                task['time_from_obj'] = parse_time_str(task.get('time_from'))
                task['time_to_obj'] = parse_time_str(task.get('time_to'))

                task['start_date'] = task.get('start_date')
                if task['start_date']:
                    try:
                        task['start_date'] = datetime.strptime(task['start_date'], '%Y-%m-%d').strftime('%d.%m.%Y')
                    except ValueError:
                        pass

                filtered.append(task)

            data[day_code] = filtered or None

        return data

    def setup_week(self, mon: str | None, tue: str | None, wed: str | None,
                   thu: str | None, fri: str | None, sat: str | None, sun: str | None,
                   mode: str):
        self.monday = mon
        self.tuesday = tue
        self.wednesday = wed
        self.thursday = thu
        self.friday = fri
        self.saturday = sat
        self.sunday = sun

        self.week_plan = True
        self.week_plan_mode = mode

    def week_xp_update_data(self, new_mode: str) -> list | None:
        xp_update = XP_MAP[new_mode] - XP_MAP[self.week_plan_mode]
        if xp_update < 0:
            return ['remove', -1 * xp_update]
        elif xp_update > 0:
            return ['add', xp_update]
        else:
            return None
