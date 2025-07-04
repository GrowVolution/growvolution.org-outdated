from website.utils.rendering import render, render_404
from website.utils.cache import request_entry_data, pop_entry
from website.data import add_model
from website.data.user import User


def confirm_notice(code: str) -> str:
    entry_code = request_entry_data(code)
    if not entry_code:
        return render_404()

    userdata = request_entry_data(entry_code)
    if not userdata:
        pop_entry(code)
        return render_404()

    name = userdata.get('first_name')
    email = userdata.get('email')

    return render('auth/confirm_notice.html', name=name, mail=email)


def handle_confirm(code: str) -> str:
    userdata = request_entry_data(code)
    if not userdata:
        return render_404()

    first_name = userdata.get('first_name')
    last_name = userdata.get('last_name')
    username = userdata.get('username')
    email = userdata.get('email')
    password = userdata.get('password')

    user = User(first_name, last_name, username, email)
    user.set_password(password)
    add_model(user)
    pop_entry(code)

    return render('auth/confirmed_notice.html')
