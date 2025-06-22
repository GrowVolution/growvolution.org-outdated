from . import start_callback
from .. import token_response
from ..login import notify
from website import DEBUG
from website.data import user as udb, add_model
from website.routing import back_to_login
from datetime import datetime
from flask import Response, session, redirect, flash, request
from urllib.parse import urlencode
from root_dir import ROOT_PATH
import os, secrets, jwt, requests, json

APPLE_KEY_ID = os.getenv('APPLE_KEY_ID')
APPLE_KEY_FILE = ROOT_PATH / 'website' / 'auth' / f'AuthKey_{APPLE_KEY_ID}.p8'
APPLE_KEY = open(APPLE_KEY_FILE).read()
APPLE_CLIENT_ID = os.getenv('APPLE_CLIENT_ID')
APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID')

APPLE_REDIRECT_URI = f"https://{'debug.' if DEBUG else ''}growvolution.org/oauth/apple/callback"
APPLE_AUTH_URI = "https://appleid.apple.com/auth/authorize"
APPLE_TOKEN_URI = "https://appleid.apple.com/auth/token"


def _sign_apple_jwt() -> str:
    headers = {
        "kid": APPLE_KEY_ID,
        "alg": "ES256"
    }
    now = int(datetime.now().timestamp())
    payload = {
        "iss": APPLE_TEAM_ID,
        "iat": now,
        "exp": now + 3600,
        "aud": "https://appleid.apple.com",
        "sub": APPLE_CLIENT_ID
    }
    return jwt.encode(payload, APPLE_KEY, algorithm="ES256", headers=headers)


def start_oauth() -> Response:
    state = secrets.token_urlsafe(16)
    session["state"] = state

    params = {
        "client_id": APPLE_CLIENT_ID,
        "redirect_uri": APPLE_REDIRECT_URI,
        "response_type": "code",
        "response_mode": "form_post",
        "scope": "name email",
        "state": state
    }

    return redirect(f"{APPLE_AUTH_URI}?{urlencode(params)}")


def oauth_callback() -> Response:
    code, state = start_callback()

    if not code or not state:
        return back_to_login()

    client_secret = _sign_apple_jwt()

    data = {
        "client_id": APPLE_CLIENT_ID,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": APPLE_REDIRECT_URI
    }

    res = requests.post(APPLE_TOKEN_URI, data=data)
    if res.status_code != 200:
        flash("Tokenaustausch mit Apple fehlgeschlagen.", "danger")
        return back_to_login()

    token_data = res.json()
    id_token = token_data.get("id_token")
    if not id_token:
        flash("Kein ID-Token von Apple erhalten.", "danger")
        return back_to_login()

    decoded = jwt.decode(id_token, options={"verify_signature": False})
    apple_id = decoded.get("sub")
    email = decoded.get("email")

    if not apple_id or not email:
        flash("Fehler beim Auslesen der Nutzerdaten.", "danger")
        return back_to_login()

    user = udb.User.query.filter_by(apple_id=apple_id).first()
    if not user:
        user = udb.User.query.filter_by(email=email).first()
        if user:
            api_flag = user.oauth_provider
            flash(f"Deine E-Mail Adresse ist bereits mit einem {api_flag.capitalize()} Account verknüpft.",
                  "warning") if api_flag \
            else flash("Es existiert bereits ein Account mit deiner E-Mail Adresse.", "warning")

            return back_to_login()

        userinfo_raw = request.form.get('user')
        userinfo = json.loads(userinfo_raw)
        first_name = userinfo.get("name", {}).get("firstName", '')
        last_name = userinfo.get("name", {}).get("lastName", '')
        username = f"{first_name}_{last_name}".lower().replace(' ', '_')

        if udb.User.query.filter_by(username=username).first():
            username = udb.randomize_username(username)

        user = udb.User(first_name, last_name, username, email, apple_id=apple_id)
        add_model(user)

    notify(user)
    return token_response({
        "id": user.id
    }, 10)