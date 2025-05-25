from website.rendering import render
from website.data import blog as blog_db
from flask import render_template
from markupsafe import Markup


def get_posts_html():
    html = ''

    counter = 1
    for post in blog_db.Blog.query.all():
        fade_direction = 'left' if counter >= 2 and counter % 2 == 0 else 'right'
        html += render_template('blog/preview_post.html', image=post.get_image_url(),
                                title=post.headline, timestamp=post.get_timestamp(), preview_text=post.summary,
                                id=post.id, fade_direction=fade_direction)
        counter += 1


    return Markup(html)


def handle_request():
    return render('blog/preview.html', posts=get_posts_html())