from shared.data import DB
from ..reaction import Reaction
from sqlalchemy.ext.hybrid import hybrid_property


class BaseModel:
    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    author_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=False)

    content = DB.Column(DB.String(512), nullable=False)
    timestamp = DB.Column(DB.DateTime, server_default=DB.func.current_timestamp())
    edited = DB.Column(DB.Boolean, default=False)

    @hybrid_property
    def author_name(self) -> str:
        author = self.author
        return f"{author.first_name} {author.last_name if not author.hide_last_name else ''}".strip()

    @hybrid_property
    def info(self) -> str:
        timestamp = self.timestamp.strftime("%d.%m.%Y %H:%M")
        edited = ' (bearbeitet)' if self.edited else ''
        return f"{timestamp}{edited}"

    @hybrid_property
    def reaction_counts(self) -> dict[str, int]:
        rows = Reaction.query.with_entities(Reaction.reaction, DB.func.count()).filter_by(
            ref_type=self.__class__.__name__.lower(),
            ref_id=self.id
        ).group_by(Reaction.reaction).all()
        return dict(rows)

    def update(self, new_content: str):
        self.content = new_content
        self.edited = True

    def set_reaction(self, user_id: int, reaction: str | None):
        existing = Reaction.query.filter_by(
            user_id=user_id,
            ref_type=self.__class__.__name__.lower(),
            ref_id=self.id
        ).first()

        if existing:
            if reaction:
                existing.reaction = reaction
            else:
                DB.session.delete(existing)
        elif reaction:
            new_reaction = Reaction(
                user_id=user_id,
                ref_type=self.__class__.__name__.lower(),
                ref_id=self.id,
                reaction=reaction
            )
            DB.session.add(new_reaction)

    def get_user_reaction(self, user_id: int) -> str | None:
        r = Reaction.query.filter_by(
            user_id=user_id,
            ref_type=self.__class__.__name__.lower(),
            ref_id=self.id
        ).first()
        return r.reaction if r else None
