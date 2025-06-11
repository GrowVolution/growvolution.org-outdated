from .. import DB
from .base import UserBase
from .info import UserInfo
from .settings import UserSettings
from .reflection import UserReflection


class User(DB.Model, UserBase, UserInfo, UserSettings, UserReflection):
    __tablename__ = 'user'
    id = DB.Column(DB.Integer, primary_key=True)

    comments = DB.relationship('Comment', back_populates='author', cascade='all, delete-orphan')
    replies = DB.relationship('Reply', back_populates='author', cascade='all, delete-orphan')

    def __init__(self, *args):
        UserBase.__init__(self, *args)
