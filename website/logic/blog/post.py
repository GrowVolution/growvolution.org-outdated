from website.rendering import render, render_404
from website.data import blog as blog_db
from markupsafe import Markup


def handle_request(blog_id: int):
    post = blog_db.Blog.query.get(blog_id)
    if not post:
        return render_404()

    return render('blog/post.html', id=blog_id, title=post.headline, image=post.get_image_url(),
                  content=Markup(post.content), author=post.author, timestamp=post.get_timestamp())