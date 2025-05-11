from website.rendering import render, render_404
from website.cache import request_entry_data
from website.data import user as udb, add_model


def confirm_notice(code):
    entry_code = request_entry_data(code)
    if not entry_code:
        return render_404()

    userdata = request_entry_data(entry_code)
    name = userdata.get('first_name')
    email = userdata.get('email')

    return render('auth/confirm_notice.html', user=name, mail=email)


def handle_confirm(code):
    userdata = request_entry_data(code)
    if not userdata:
        return render_404()

    first_name = userdata.get('first_name')
    last_name = userdata.get('last_name')
    username = userdata.get('username')
    email = userdata.get('email')
    password = userdata.get('password')

    user = udb.User(first_name, last_name, username, email, password=password)
    add_model(user)

    return render('auth/confirmed_notice.html')
