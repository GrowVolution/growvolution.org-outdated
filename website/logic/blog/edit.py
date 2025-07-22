from website.data import blog as blog_db, cloudinary
from flask import request, abort


def handle_request(user, blog_id: int):
    post = blog_db.Blog.query.get(blog_id)
    if not post:
        return 'Blog ID existiert nicht!', 500

    if not post.author == user.username:
        return abort(401)

    form = request.form

    title = form.get('title')
    summary = form.get('summary')
    content = form.get('content')

    post.update_data(title, summary, content)

    image = request.files.get('image')
    if image:
        cloudinary.upload_asset(image, public_id=post.image, overwrite=True)

    return '', 200