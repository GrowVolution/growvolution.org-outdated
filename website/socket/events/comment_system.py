from . import register_event, require_user
from .. import emit_html, socket_flash
from website.data import comment as comment_db, reply as reply_db, blog as blog_db, add_model, delete_model, commit
from website.logic.comments import comment as comment_logic, reply as reply_logic


@register_event('add_comment')
@require_user(True)
def handle_comment(user, data):
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


@register_event('add_reply')
@require_user(True)
def handle_reply(user, data):
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


def _ref_author(user, ref) -> bool:
    if user != ref.author:
        socket_flash("Hierzu bist du nicht berechtigt!", 'danger')
        return False
    return True


@register_event('add_like')
@require_user(True)
def handle_like(user, data):
    ref = _action_ref(data)
    if ref.like(user.id):
        commit()


@register_event('remove_like')
@require_user(True)
def handle_unlike(user, data):
    ref = _action_ref(data)
    if ref.unlike(user.id):
        commit()


@register_event('comment_system_edit')
@require_user(True)
def handle_edit(user, data):
    ref = _action_ref(data)
    if _ref_author(user, ref):
        ref.update(data.get('text'))
        commit()


@register_event('comment_system_delete')
@require_user(True)
def handle_delete(user, data):
    ref = _action_ref(data)
    if _ref_author(user, ref):
        delete_model(ref)


@register_event('reply_request')
def handle_reply_request(comment_id):
    comment = comment_db.Comment.query.get(int(comment_id))
    emit_html(reply_logic.get_replies_html(comment))
