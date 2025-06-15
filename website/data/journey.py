from . import DB
from datetime import datetime, time


class Journey(DB.Model):
    __tablename__ = 'journey'
    uid = DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=False, primary_key=True)
    timestamp = DB.Column(DB.DateTime, nullable=False, primary_key=True)

    # Daily Tracking
    mood_level = DB.Column(DB.Integer)
    worked_on_goal = DB.Column(DB.Boolean)
    short_note = DB.Column(DB.String(200))
    quick_motivation = DB.Column(DB.String(150))
    motivation_type = DB.Column(DB.String(12))

    # Weekly Tracking
    # TODO: content

    # Quarter Tracking
    # ...

    def __init__(self, user_id: int):
        self.uid = user_id
        self.timestamp = datetime.combine(datetime.now().date(), time.min)

    def daily_track(self, mood_level: int , worked_on_goal: bool, short_note: str | None,
                    quick_motivation: str | None, motivation_type: str | None):
        self.mood_level = mood_level
        self.worked_on_goal = worked_on_goal
        self.short_note = short_note
        self.quick_motivation = quick_motivation
        self.motivation_type = motivation_type

    def weekly_track(self):
        pass

    def quarter_track(self):
        pass

    #...
