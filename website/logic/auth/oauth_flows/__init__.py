from flask import request, flash, session


def start_callback() -> tuple[str | None, str | None]:
    if request.method == "POST":
        code = request.form.get("code")
        state = request.form.get("state")
    else:
        code = request.args.get("code")
        state = request.args.get("state")

    if state != session.get('state'):
        flash("OAuth Status ungültig!", 'danger')
        return None, None

    if not code:
        flash("OAuth Code fehlt!", 'danger')
        return None, None

    return code, state
