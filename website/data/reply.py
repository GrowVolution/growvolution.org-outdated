from . import DB, commit
from sqlalchemy import exists, and_
from markupsafe import Markup
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .comment import Comment

LIKED = DB.Table('liked_replies', DB.Column('uid', DB.Integer, DB.ForeignKey('user.id'), primary_key=True),
                 DB.Column('rid', DB.Integer, DB.ForeignKey('reply.id'), primary_key=True))

def _mention_html(mention: int | str, name: str) -> str:
    return f"<a href='#reply-{mention}' class='text-dark text-hover-muted text-decoration-none'><i>@{name}</i></a>"


class Reply(DB.Model):
    __tablename__ = 'reply'
    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    author_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=False)
    comment_id = DB.Column(DB.Integer, DB.ForeignKey('comment.id'), nullable=False)

    content = DB.Column(DB.String(512), nullable=False)
    mention = DB.Column(DB.Integer, default=None)
    timestamp = DB.Column(DB.DateTime, server_default=DB.func.current_timestamp())
    edited = DB.Column(DB.Boolean, default=False)

    likes = DB.Column(DB.Integer, default=0)

    author = DB.relationship('User', back_populates='replies')
    comment = DB.relationship('Comment', back_populates='replies')

    def __init__(self, author: 'User', comment: 'Comment', content: str, mention: int | None = None):
        self.author = author
        self.comment = comment
        self.content = content
        self.mention = mention

    def get_content(self):
        if self.mention:
            ref = self.query.get(self.mention)
            if ref:
                user = ref.author
                mention = _mention_html(self.mention, f"{user.first_name} {user.last_name}")
            else:
                mention = _mention_html('deleted', "Antwort gelöscht")
            return Markup(f"{mention} {self.content}")

        return self.content

    def get_info(self) -> str:
        timestamp = self.timestamp.strftime("%d.%m.%Y %H:%M")
        edited = ' (bearbeitet)' if self.edited else ''
        return f"{timestamp}{edited}"

    def update(self, new_content: str) -> None:
        self.content = new_content
        self.edited = True
        commit()

    def like(self, by_user_id: int) -> None:
        if not self.has_liked(by_user_id):
            DB.session.execute(
                LIKED.insert().values(uid=by_user_id, rid=self.id)
            )
            self.likes += 1
            commit()

    def unlike(self, by_user_id: int) -> None:
        if self.has_liked(by_user_id):
            DB.session.execute(
                LIKED.delete().where(and_(LIKED.c.uid == by_user_id, LIKED.c.rid == self.id))
            )
            self.likes = max(0, self.likes - 1)
            commit()

    def has_liked(self, user_id: int) -> bool:
        return DB.session.query(
            exists().where(and_(LIKED.c.uid == user_id, LIKED.c.rid == self.id))
        ).scalar()
