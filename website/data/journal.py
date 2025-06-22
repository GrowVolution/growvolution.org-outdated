from . import DB
from website.utils import normalize_timestamp
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
import json


class JournalData(DB.Model):
    __tablename__ = 'journal_data'
    uid = DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=False, primary_key=True)
    timestamp = DB.Column(DB.DateTime, nullable=False, primary_key=True)

    content_json_str = DB.Column(DB.Text)

    @hybrid_property
    def content_data(self) -> dict | None:
        try:
            return json.loads(self.content_json_str)
        except ValueError:
            return None

    def __init__(self, user_id: int, content_json_str: str):
        self.uid = user_id
        self.content_json_str = content_json_str
        self.timestamp = normalize_timestamp(datetime.now())
