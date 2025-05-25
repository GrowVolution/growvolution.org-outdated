from . import DB, cloudinary


class Blog(DB.Model):
    __tablename__ = 'blog'
    id = DB.Column(DB.Integer, primary_key=True)

    headline = DB.Column(DB.String(64), nullable=False)
    image = DB.Column(DB.String(64), nullable=False)
    summary = DB.Column(DB.Text, nullable=False)
    content = DB.Column(DB.Text, nullable=False)

    author = DB.Column(DB.String(96), nullable=False)
    timestamp = DB.Column(DB.DateTime, nullable=False, server_default=DB.func.current_timestamp())

    def __init__(self, headline: str, image_id: str, summary: str, content: str, author: str):
        self.headline = headline
        self.image = image_id
        self.summary = summary
        self.content = content
        self.author = author

    def get_image_url(self) -> str | None:
        return cloudinary.retrieve_asset_url(self.image)

    def get_timestamp(self) -> str:
        return self.timestamp.strftime("%d.%m.%Y %H:%M")
