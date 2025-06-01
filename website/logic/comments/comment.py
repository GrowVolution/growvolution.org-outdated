from website.rendering import render
from website.logic.auth.verification import get_user
from website.data.comment import Comment
from website.data.blog import Blog
from website.data.user import User
from markupsafe import Markup


def render_comment(comment: Comment, user: User, render_index: int = 1) -> str:
    author = comment.author
    author_name = f"{author.first_name} {author.last_name}"
    is_author = author == user
    return render('comments/comment.html', id=comment.id, render_index=render_index, author=author_name,
                  picture=author.get_picture_url(), comment_info=comment.get_info(), comment_text=comment.content,
                  like_count=comment.likes, liked=comment.has_liked(user.id), is_author=is_author,
                  reply_count=comment.reply_count)


def get_comments_html(post: Blog) -> Markup:
    html = ''

    index = 1
    user = get_user()
    for comment in post.comments:
        html += render_comment(comment, user, index)
        index += 1

    return Markup(html)
