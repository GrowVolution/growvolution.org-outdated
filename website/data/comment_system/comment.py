from . import BaseModel
from shared.data import DB
from sqlalchemy.ext.hybrid import hybrid_property
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..user import User
    from ..blog import Blog


class Comment(DB.Model, BaseModel):
    __tablename__ = 'comment'
    blog_id = DB.Column(DB.Integer, DB.ForeignKey('blog.id'))

    replies = DB.relationship('Reply', backref='comment', cascade='all, delete-orphan')

    def __init__(self, author: 'User', blog: Optional['Blog'], content: str):
        self.author = author
        self.blog = blog
        self.content = content

    @hybrid_property
    def reply_count(self) -> int:
        return len(self.replies)
