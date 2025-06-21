from website.rendering import render
from website.logic.auth.verification import get_user
from website.data.reply import Reply
from website.data.comment import Comment
from website.data.user import User
from markupsafe import Markup


def render_reply(reply: Reply, user: User, render_index: int = 0) -> str:
    return render('comments/reply.html', user, reply=reply, first_reply=render_index == 1,
                  liked=reply.has_liked(user.id), is_author=reply.author == user)


def get_replies_html(comment: Comment) -> Markup:
    html = ''

    index = 1
    user = get_user()
    for reply in comment.replies:
        html += render_reply(reply, user, index)
        index += 1

    return Markup(html)
