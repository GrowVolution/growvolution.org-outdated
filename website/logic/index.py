from website.utils.rendering import render
from website.data import blog as blog_db
from .auth import get_user
from .user.profile import user_dashboard
from markupsafe import Markup
from flask import render_template


def get_posts_html():
    html = ''

    counter = 1
    for post in blog_db.Blog.query.order_by(blog_db.Blog.id.desc()).all():
        html += render_template('site/index_blog_preview.html',
                                delay=counter*100, post=post)
        counter += 1

        if counter > 3:
            break

    return Markup(html)


def handle_request():
    user = get_user()
    if user:
        return user_dashboard()

    return render('site/index.html', posts=get_posts_html())