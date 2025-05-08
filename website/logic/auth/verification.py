from LIBRARY import *
from website import APP

def start_callback():
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

def empty_token():
    response = make_response(redirect(request.path))
    response.set_cookie('token', '', expires=0)
    return response

def token_response(data, expiration_days, name='token', response=redirect('/'), status=200):
    expiration = timedelta(days=expiration_days)
    max_age = expiration_days * 24 * 60 * 60

    data['exp'] = datetime.now() + expiration
    token = jwt.encode(data, APP.config['SECRET_KEY'], algorithm='HS256')

    res = make_response(response, status)
    res.set_cookie(name, token, httponly=True, secure=True, max_age=max_age)

    return res

def _decoded_token(token):
    try:
        return jwt.decode(token, key=APP.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except jwt.InvalidSignatureError:
        return None

def captcha_status():
    decoded_token = _decoded_token(request.cookies.get('captcha_token'))
    return decoded_token.get('status') if decoded_token else 'unverified'
