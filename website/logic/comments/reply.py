from website.rendering import render
from website.logic.auth.verification import get_user
from website.data.reply import Reply
from website.data.comment import Comment
from website.data.user import User
from markupsafe import Markup


def render_reply(reply: Reply, user: User, render_index: int = 0) -> str:
    author = reply.author
    author_name = f"{author.first_name} {author.last_name}"
    is_author = author == user
    return render('comments/reply.html', id=reply.id, first_reply=render_index == 1,
                  picture=author.get_picture_url(), author=author_name, reply_info=reply.get_info(),
                  reply_text=reply.get_content(), like_count=reply.likes, liked=reply.has_liked(user.id),
                  is_author=is_author)


def get_replies_html(comment: Comment) -> Markup:
    html = ''

    index = 1
    user = get_user()
    for reply in comment.replies:
        html += render_reply(reply, user, index)
        index += 1

    return Markup(html)
