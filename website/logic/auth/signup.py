from website.utils.rendering import render
from website.utils.cache import add_entry
from website.utils.mail_service import confirmation_mail
from flask import Response, request, redirect


def handle_request() -> Response | str:
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        data = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'email': email,
            'password': password
        }

        code = add_entry(data, 10)
        confirmation_mail(email, first_name, code)

        entry_code = add_entry(code, 10)

        return redirect(f'/notice/confirm/{entry_code}')

    return render('auth/signup.html')