from . import BaseModel
from shared.data import DB
from markupsafe import Markup
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..user import User
    from .comment import Comment

def _mention_html(mention: int | str, name: str) -> str:
    return f"<a href='#reply-{mention}' class='text-dark text-hover-muted text-decoration-none'><i>@{name}</i></a>"


class Reply(DB.Model, BaseModel):
    __tablename__ = 'reply'
    comment_id = DB.Column(DB.Integer, DB.ForeignKey('comment.id'), nullable=False)
    mention = DB.Column(DB.Integer, default=None)

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
