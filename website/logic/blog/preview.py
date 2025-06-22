from website.utils.rendering import render
from website.data import blog as blog_db
from markupsafe import Markup


def get_posts_html():
    html = ''

    counter = 1
    for post in blog_db.Blog.query.order_by(blog_db.Blog.id.desc()).all():
        fade_direction = 'left' if counter >= 2 and counter % 2 == 0 else 'right'
        html += render('blog/preview_post.html', post=post, fade_direction=fade_direction)
        counter += 1

    return Markup(html)


def handle_request():
    return render('blog/preview.html', posts=get_posts_html())