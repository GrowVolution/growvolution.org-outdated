from website.rendering import render
from website.logic.auth.verification import get_user
from website.data.comment import Comment
from website.data.blog import Blog
from website.data.user import User
from markupsafe import Markup


def render_comment(comment: Comment, user: User, render_index: int = 1) -> str:
    return render('comments/comment.html', comment=comment, render_index=render_index,
                  is_author=comment.author == user, liked=comment.has_liked(user.id))


def get_comments_html(post: Blog) -> Markup:
    html = ''

    index = 1
    user = get_user()
    for comment in post.comments:
        html += render_comment(comment, user, index)
        index += 1

    return Markup(html)
