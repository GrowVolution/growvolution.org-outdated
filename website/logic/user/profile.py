from website.rendering import render, render_404
from website.cache import request_entry_data, pop_entry, add_entry
from website.logic.auth.verification import get_user
from LIBRARY import back_to_login
from flask import jsonify
import pyotp, base64, qrcode, io


def handle_mail_change(code: str):
    data = request_entry_data(code)
    if not data:
        return render_404()

    user = data.get('user')
    user.set_email(data['email'])
    pop_entry(code)

    return render('user/mail_change_confirmed.html')


def twofa_setup():
    user = get_user()
    if not user:
        return jsonify({'error': 'Nicht authentifiziert'}), 401

    secret = pyotp.random_base32()
    issuer = "GrowVolution"

    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.username, issuer_name=issuer)

    qr_img = qrcode.make(uri)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    qr_data_url = f"data:image/png;base64,{qr_base64}"

    code = add_entry(secret, 10)

    return jsonify({
        'code': code,
        'secret': secret,
        'qr': qr_data_url
    })


def handle_request():
    user = get_user()
    if not user:
        return back_to_login()

    return render('user/profile.html', user=user)
