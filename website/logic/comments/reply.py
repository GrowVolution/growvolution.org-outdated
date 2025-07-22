from website.utils.rendering import render
from website.logic.auth import get_user
from website.data.comment_system.reply import Reply
from website.data.comment_system.comment import Comment
from website.data.user import User
from markupsafe import Markup


def render_reply(reply: Reply, user: User, render_index: int = 0) -> str:
    return render('comments/reply.html', reply=reply, first_reply=render_index == 1,
                  is_author=reply.author == user, reaction_type=reply.get_user_reaction(user.id) if user else None)


def get_replies_html(comment: Comment) -> Markup:
    html = ''

    index = 1
    user = get_user()
    for reply in comment.replies:
        html += render_reply(reply, user, index)
        index += 1

    return Markup(html)
