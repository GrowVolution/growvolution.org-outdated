from shared.data import DB, commit
from .base import UserBase
from .info import UserInfo
from .settings import UserSettings
from .reflection import UserReflection
from .journey import UserJourney
from .week import UserWeek, RELIABILITY_XP_MAP


def update_user_scores():
    from website import APP
    with APP.app_context():
        for user in User.query.all():
            if not user.week_plan:
                continue

            max_score = RELIABILITY_XP_MAP[user.week_plan_mode]
            score = user.plan_reliability_today * max_score
            user.add_xp(int(score))

        commit()


class User(DB.Model, UserBase, UserInfo, UserSettings, UserReflection, UserJourney, UserWeek):
    __tablename__ = 'user'
    id = DB.Column(DB.Integer, primary_key=True)

    comments = DB.relationship('Comment', backref='author', cascade='all, delete-orphan')
    replies = DB.relationship('Reply', backref='author', cascade='all, delete-orphan')

    journey = DB.relationship('Journey', backref='user', cascade='all, delete-orphan')
    journal = DB.relationship('JournalData', backref='user', cascade='all, delete-orphan')

    def __init__(self, *args):
        UserBase.__init__(self, *args)
