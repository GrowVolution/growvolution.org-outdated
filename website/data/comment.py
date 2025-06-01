from . import DB, commit
from sqlalchemy import exists, and_
from sqlalchemy.ext.hybrid import hybrid_property
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .user import User
    from .blog import Blog

LIKED = DB.Table('liked_comments', DB.Column('uid', DB.Integer, DB.ForeignKey('user.id'), primary_key=True),
                 DB.Column('cid', DB.Integer, DB.ForeignKey('comment.id'), primary_key=True))


class Comment(DB.Model):
    __tablename__ = 'comment'
    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    author_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=False)
    blog_id = DB.Column(DB.Integer, DB.ForeignKey('blog.id'))

    content = DB.Column(DB.String(512), nullable=False)
    timestamp = DB.Column(DB.DateTime, server_default=DB.func.current_timestamp())
    edited = DB.Column(DB.Boolean, default=False)

    author = DB.relationship('User', back_populates='comments')
    blog = DB.relationship('Blog', back_populates='comments')

    likes = DB.Column(DB.Integer, default=0)

    replies = DB.relationship('Reply', back_populates='comment', cascade='all, delete-orphan')

    def __init__(self, author: 'User', blog: Optional['Blog'], content: str):
        self.author = author
        self.blog = blog
        self.content = content

    def get_info(self) -> str:
        timestamp = self.timestamp.strftime("%d.%m.%Y %H:%M")
        edited = ' (bearbeitet)' if self.edited else ''
        return f"{timestamp}{edited}"

    @hybrid_property
    def reply_count(self) -> int:
        return len(self.replies)

    def update(self, new_content: str):
        self.content = new_content
        self.edited = True
        commit()

    def like(self, by_user_id: int) -> None:
        if not self.has_liked(by_user_id):
            DB.session.execute(
                LIKED.insert().values(uid=by_user_id, cid=self.id)
            )
            self.likes += 1
            commit()

    def unlike(self, by_user_id: int) -> None:
        if self.has_liked(by_user_id):
            DB.session.execute(
                LIKED.delete().where(and_(LIKED.c.uid == by_user_id, LIKED.c.cid == self.id))
            )
            self.likes = max(0, self.likes - 1)
            commit()

    def has_liked(self, user_id: int) -> bool:
        return DB.session.query(
            exists().where(and_(LIKED.c.uid == user_id, LIKED.c.cid == self.id))
        ).scalar()
