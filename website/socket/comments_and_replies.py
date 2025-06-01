from website.data import comment as comment_db, reply as reply_db, blog as blog_db, add_model, delete_model
from website.logic.auth.verification import get_user
from website.logic.comments import comment as comment_logic, reply as reply_logic


def handle_comment(data):
    from . import emit_html
    user = get_user()
    ref_type = data.get('type')

    if ref_type == 'blog':
        post_id = int(data.get('ref', 0))
        post = blog_db.Blog.query.get(post_id)
        comment = comment_db.Comment(user, post, data.get('text'))
        add_model(comment)
        emit_html(comment_logic.render_comment(comment, user))

    else:
        # TODO: Not implemented yet
        pass


def handle_reply(data):
    from . import emit_html
    user = get_user()
    comment_id = int(data.get('comment', 0))
    comment = comment_db.Comment.query.get(comment_id)
    reply = reply_db.Reply(user, comment, data.get('content'), data.get('mention'))
    add_model(reply)
    emit_html(reply_logic.render_reply(reply, user))


def _action_ref(data):
    ref_type = data.get('type')

    if ref_type == 'comment':
        comment_id = int(data.get('ref', 0))
        ref = comment_db.Comment.query.get(comment_id)

    else:
        reply_id = int(data.get('ref', 0))
        ref = reply_db.Reply.query.get(reply_id)

    return ref


def handle_like(data):
    user = get_user()
    ref = _action_ref(data)
    ref.like(user.id)


def handle_unlike(data):
    user = get_user()
    ref = _action_ref(data)
    ref.unlike(user.id)


def handle_edit(data):
    ref = _action_ref(data)
    ref.update(data.get('text'))


def handle_delete(data):
    ref = _action_ref(data)
    delete_model(ref)


def handle_reply_request(comment_id):
    from . import emit_html
    comment = comment_db.Comment.query.get(int(comment_id))
    emit_html(reply_logic.get_replies_html(comment))
