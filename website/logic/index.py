from website.rendering import render
from website.data import blog as blog_db
from .auth.verification import get_user
from .user.profile import user_dashboard
from markupsafe import Markup
from flask import render_template


def get_posts_html():
    html = ''

    counter = 1
    for post in blog_db.Blog.query.order_by(blog_db.Blog.id.desc()).all():
        html += render_template('site/index_blog_preview.html', delay=counter*100,
                                title=post.headline, preview_text=post.summary, id=post.id)
        counter += 1

        if counter > 3:
            break

    # Just for the beginning
    while counter <= 3:
        html += render_template('site/index_blog_preview.html', delay=counter*100,
                                title=f"Blogtitel {counter}", preview_text="Dieser Beitrag existiert noch nicht...",
                                id=counter)
        counter += 1

    return Markup(html)


def handle_request():
    user = get_user()
    if user:
        return user_dashboard(user)

    return render('site/index.html', posts=get_posts_html())