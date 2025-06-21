from . import DB


class Reaction(DB.Model):
    __tablename__ = 'reaction'
    user_id = DB.Column(DB.Integer, nullable=False, primary_key=True)
    ref_type = DB.Column(DB.String(32), nullable=False, primary_key=True)
    ref_id = DB.Column(DB.Integer, nullable=False, primary_key=True)

    reaction = DB.Column(DB.String(32), nullable=False)

    def __init__(self, user_id: int, ref_type: str, ref_id: int, reaction: str):
        self.user_id = user_id
        self.ref_type = ref_type
        self.ref_id = ref_id
        self.reaction = reaction
