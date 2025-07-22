from . import require_user, require_admin, METHODS
from website.logic.blog import preview, create, edit, post
from flask import Blueprint

blog = Blueprint('blog', __name__)


@blog.route('/')
def main():
    return preview.handle_request()


@blog.route('/<blog_id>')
def blog_post(blog_id):
    return post.handle_request(blog_id)


@blog.route('/<blog_id>/edit', methods=METHODS.POST)
@require_user(True)
def blog_edit(user, blog_id):
    return edit.handle_request(user, blog_id)


@blog.route('/new', methods=METHODS.ALL)
@require_admin(False)
def new_blog_post():
    return create.handle_request()
