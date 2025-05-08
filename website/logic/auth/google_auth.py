from LIBRARY import *
from website import DEBUG
from website.data import add_model, user as udb
from .verification import token_response, start_callback

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT')
GOOGLE_REDIRECT = f"https://{'debug.' if DEBUG else ''}growvolution.org/oauth/google/callback"
GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"

GOOGLE_SECRET = os.getenv('GOOGLE_OAUTH_SECRET')
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO = "https://www.googleapis.com/oauth2/v2/userinfo"

def start_oauth():
    state = secrets.token_urlsafe(16)
    session['state'] = state
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT,
        "response_type": "code",
        "state": state,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    return redirect(f"{GOOGLE_AUTH_URI}?{urlencode(params)}")


def oauth_callback():
    code, state = start_callback()

    if not code or not state:
        return back_to_login()

    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_SECRET,
        "redirect_uri": GOOGLE_REDIRECT,
        "grant_type": "authorization_code"
    }
    token_res = requests.post(GOOGLE_TOKEN_URI, data=token_data)
    if token_res.status_code != 200:
        flash("Tokenaustasch fehlgeschlagen!", 'danger')
        return back_to_login()

    tokens = token_res.json()
    access_token = tokens.get('access_token')

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    userinfo_res = requests.get(GOOGLE_USERINFO, headers=headers)
    if userinfo_res.status_code != 200:
        flash("Fehler beim Laden der Benutzerdaten!", 'danger')
        return back_to_login()

    userinfo = userinfo_res.json()

    google_id = userinfo.get('id')
    email = userinfo.get('email')

    if not email or not google_id:
        flash("Ungültige Benutzerdaten!", 'danger')
        return back_to_login()

    user = udb.User.query.filter_by(google_id=google_id).first()
    if not user:
        user = udb.User.query.filter_by(email=email).first()
        if user:
            api_flag = 'Apple' if user.apple_id else (
                'Microsoft' if user.microsoft_id else None
            )
            flash(f"Deine E-Mail Adresse ist bereits mit einem {api_flag} Account verknüpft.",
                  "warning") if api_flag \
                else flash("Es existiert bereits ein Account mit deiner E-Mail Adresse.",
                           "warning")
            return back_to_login()

        first_name = userinfo.get('given_name')
        last_name = userinfo.get('family_name')
        username = f"{first_name} {last_name}".lower().replace(' ', '_')
        picture = userinfo.get('picture')

        if udb.User.query.filter_by(username=username).first():
            username = udb.randomize_username(username)

        user = udb.User(first_name, last_name, username, email, picture, str(google_id))
        add_model(user)

    return token_response({
        "id": user.id
    }, 10)