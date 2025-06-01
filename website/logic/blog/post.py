from website.rendering import render, render_404
from website.data import blog as blog_db
from ..auth.verification import get_user
from ..comments.comment import get_comments_html
from markupsafe import Markup


def handle_request(blog_id: int):
    post = blog_db.Blog.query.get(blog_id)
    if not post:
        return render_404()

    user = get_user()
    creator = user and user.username == post.author

    return render('blog/post.html', id=blog_id, title=post.headline, image=post.get_image_url(),
                  content=Markup(post.content), post_info=post.get_info(), creator=creator, summary=post.summary if creator else '',
                  comments=get_comments_html(post))
