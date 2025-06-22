from .. import DB
from website.utils import parse_time_str
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta
import json

XP_MAP = {
    'simple': 25,
    'medium': 50,
    'free': 75
}

RELIABILITY_XP_MAP = {
    'simple': 5,
    'medium': 10,
    'free': 15
}

DAY_CODES = ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so']


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
    def active_week_tasks(self) -> dict[str, list[dict] | None]:
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        today_str = today.isoformat()

        data = {}
        for day_code, attr in zip(
                DAY_CODES,
                ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        ):
            raw = getattr(self, attr)
            if not raw:
                data[day_code] = None
                continue

            if self.week_plan_mode == 'simple':
                if raw == 'restday':
                    data[day_code] = 'restday'
                    continue

                parts = raw.split('|')
                data[day_code] = {
                    'label': parts[0],
                    'done': today_str == parts[1] if len(parts) > 1 else False
                }
                continue

            if raw == 'restday':
                data[day_code] = 'restday'
                continue

            try:
                tasks = json.loads(raw)
            except json.JSONDecodeError:
                data[day_code] = None
                continue

            if self.week_plan_mode == 'medium':
                parsed = []
                for task in tasks:
                    parts = task.split('|')
                    task_data = {
                        'label': parts[0],
                        'done': today_str == parts[1] if len(parts) > 1 else False
                    }
                    parsed.append(task_data)
                data[day_code] = parsed
                continue

            filtered = []
            for task in tasks:
                try:
                    start_date = datetime.strptime(task.get('start_date', ''), '%Y-%m-%d').date()
                    frequency = task.get('frequency', 'weekly')
                    multi = task.get('multi') is True or task.get('multi') == '1'
                    weekdays = task.get('weekdays') or []
                except (ValueError, TypeError, AttributeError):
                    continue

                weekday_index = DAY_CODES.index(day_code)
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

                if 'start_date' in task:
                    try:
                        task['start_date'] = datetime.strptime(task['start_date'], '%Y-%m-%d').strftime('%d.%m.%Y')
                    except ValueError:
                        pass

                done_str = task.get('done')
                task['done'] = done_str == today_str

                filtered.append(task)

            data[day_code] = filtered or None

        return data

    @hybrid_property
    def day_code_today(self) -> str:
        today = datetime.now().date()
        weekday_index = today.weekday()
        return DAY_CODES[weekday_index]

    @hybrid_property
    def day_codes_today(self) -> list[str]:
        today = datetime.now().date()
        weekday_index = today.weekday()
        return DAY_CODES[:weekday_index + 1]

    @hybrid_property
    def tasks_done_count(self) -> int:
        active_tasks = self.active_week_tasks
        count = 0

        for day_tasks in active_tasks.values():
            if isinstance(day_tasks, list):
                for task in day_tasks:
                    if task.get('done') is True:
                        count += 1

        return count

    @hybrid_property
    def week_reliability_score(self) -> int:
        count = self.get_task_count(self.day_codes_today)
        return ((self.tasks_done_count / count) * 100) if count != 0 else 0

    @hybrid_property
    def plan_reliability_today(self) -> int:
        today_code = self.day_code_today
        active_tasks = self.active_week_tasks.get(today_code)

        if not isinstance(active_tasks, list) or not active_tasks:
            return 0

        done = sum(1 for task in active_tasks if task.get('done') is True)
        total = len(active_tasks)

        return int(done / total) if total else 0


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

    def get_task_count(self, days: list[str]) -> int:
        mode = self.week_plan_mode
        week = self.active_week_tasks

        if mode == 'simple':
            return sum(1 for day in days if week.get(day) not in [None, 'restday'])

        elif mode in {'medium', 'free'}:
            return sum(len(week[day]) for day in days if isinstance(week.get(day), list))

        return 0


    def set_task_done(self, task_id: str):
        today = datetime.now().date()
        weekday_map = {
            'mo': 0, 'di': 1, 'mi': 2,
            'do': 3, 'fr': 4, 'sa': 5, 'so': 6
        }

        parts = task_id.split('-')
        day_code = parts[0]
        index = int(parts[1]) if len(parts) > 1 else None

        if today.weekday() != weekday_map.get(day_code):
            return

        mode = self.week_plan_mode
        attr = {
            'mo': 'monday', 'di': 'tuesday', 'mi': 'wednesday',
            'do': 'thursday', 'fr': 'friday', 'sa': 'saturday', 'so': 'sunday'
        }.get(day_code)

        raw = getattr(self, attr)
        if not raw or raw == 'restday':
            return

        try:
            tasks = json.loads(raw)
        except (ValueError, TypeError):
            tasks = raw

        if mode == 'simple':
            tasks = f"{tasks}|{today.isoformat()}"
        elif isinstance(tasks, list) and index is not None and 0 <= index < len(tasks):
            if isinstance(tasks[index], dict):
                tasks[index]['done'] = today.isoformat()
            else:
                tasks[index] = f"{tasks[index]}|{today.isoformat()}"
        else:
            return

        setattr(self, attr, json.dumps(tasks) if mode != 'simple' else tasks)
