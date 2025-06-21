from website.rendering import render, render_404
from website.data import blog as blog_db
from ..auth.verification import get_user
from ..comments.comment import get_comments_html


def handle_request(blog_id: int):
    post = blog_db.Blog.query.get(blog_id)
    if not post:
        return render_404()

    return render('blog/post.html', get_user(), post=post, comments=get_comments_html(post))
