from . import DB
from .helpers import normalize_timestamp
from datetime import datetime


class Journey(DB.Model):
    __tablename__ = 'journey'
    uid = DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=False, primary_key=True)
    timestamp = DB.Column(DB.DateTime, nullable=False, primary_key=True)

    step_type = DB.Column(DB.String(16), nullable=False, default='daily')

    # Daily Tracking
    mood_level = DB.Column(DB.Integer)
    worked_on_goal = DB.Column(DB.Boolean)
    short_note = DB.Column(DB.String(200))
    quick_motivation = DB.Column(DB.String(150))
    motivation_type = DB.Column(DB.String(12))

    # Weekly Tracking
    week_goal = DB.Column(DB.Text)
    week_good = DB.Column(DB.String(300))
    week_bad = DB.Column(DB.String(300))

    # Quarter Tracking
    # ...

    def __init__(self, user_id: int):
        self.uid = user_id
        self.timestamp = normalize_timestamp(datetime.now())

    def daily_track(self, mood_level: int , worked_on_goal: bool, short_note: str | None,
                    quick_motivation: str | None, motivation_type: str | None):
        self.mood_level = mood_level
        self.worked_on_goal = worked_on_goal
        self.short_note = short_note
        self.quick_motivation = quick_motivation
        self.motivation_type = motivation_type

        self.step_type = 'daily'

    def weekly_track(self, goal: str, good: str, bad: str):
        self.week_goal = goal
        self.week_good = good
        self.week_bad = bad

        self.step_type = 'weekly'

    def quarter_track(self):
        pass

    #...
