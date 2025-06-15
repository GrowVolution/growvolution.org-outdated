from website import DEBUG
from website.data import user as udb, add_model
from .verification import token_response, start_callback
from .login import notify
from LIBRARY import back_to_login
from flask import Response, session, redirect, flash
from urllib.parse import urlencode
import os, secrets, jwt, requests

MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_SECRET")

MICROSOFT_REDIRECT_URI = f"https://{'debug.' if DEBUG else ''}growvolution.org/oauth/microsoft/callback"
MICROSOFT_AUTH_URI = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
MICROSOFT_TOKEN_URI = "https://login.microsoftonline.com/common/oauth2/v2.0/token"


def start_oauth() -> Response:
    state = secrets.token_urlsafe(16)
    session["state"] = state

    params = {
        "client_id": MICROSOFT_CLIENT_ID,
        "redirect_uri": MICROSOFT_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "response_mode": "form_post"
    }

    return redirect(f"{MICROSOFT_AUTH_URI}?{urlencode(params)}")


def oauth_callback() -> Response:
    code, state = start_callback()

    if not code or not state:
        return back_to_login()

    data = {
        "client_id": MICROSOFT_CLIENT_ID,
        "client_secret": MICROSOFT_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": MICROSOFT_REDIRECT_URI
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    res = requests.post(MICROSOFT_TOKEN_URI, data=data, headers=headers)
    if res.status_code != 200:
        flash("Tokenaustausch mit Microsoft fehlgeschlagen.", "danger")
        return back_to_login()

    token_data = res.json()
    id_token = token_data.get("id_token")
    if not id_token:
        flash("Kein ID-Token von Microsoft erhalten.", "danger")
        return back_to_login()

    decoded = jwt.decode(id_token, options={"verify_signature": False})
    microsoft_id = decoded.get("sub")
    email = decoded.get("email") or decoded.get("preferred_username")

    if not microsoft_id or not email:
        flash("Fehler beim Auslesen der Nutzerdaten.", "danger")
        return back_to_login()

    user = udb.User.query.filter_by(microsoft_id=microsoft_id).first()
    if not user:
        user = udb.User.query.filter_by(email=email).first()
        if user:
            api_flag = user.oauth_provider
            flash(f"Deine E-Mail Adresse ist bereits mit einem {api_flag.capitalize()} Account verknüpft.",
                  "warning") if api_flag \
            else flash("Es existiert bereits ein Account mit deiner E-Mail Adresse.","warning")

            return back_to_login()

        name = decoded.get("name")
        first_name, last_name = (name.split(" ", 1) + [""])[:2]
        username = name.lower().replace(" ", "_") if '@' in email else email
        email = email if '@' in email else "placeholder"

        if udb.User.query.filter_by(username=username).first():
            username = udb.randomize_username(username)

        user = udb.User(first_name, last_name, username, email, microsoft_id=microsoft_id)
        add_model(user)

    notify(user)
    return token_response({
        "id": user.id
    }, 10)
