from shared.mail_service import send

BASE_HTML = """<DOCTYPE html>
<html lang="de">
    <head>
        <meta charset="utf-8">
        <title>GrowV Admin API</title>
    </head>
    <body>
        {content}
    </body>
</html>
"""


def token_mail(receiver: str, name: str, token: str):
    content = f"""
        Hey {name}!<br><br>
        Wir freuen uns dir mitteilen zu können, dass die Administration deinem Antrag zugestimmt hat.
        Du bist nun dazu berechtigt dir einen Zugang zur API anzulegen. Bitte nutze hierzu unser
        <a href="#">Verwaltungstool</a>. Setze hierzu beim Login einen Haken bei 'Neu anlegen'. Zum
        anlegen des Accounts benötigst du folgendes Token:<br><br>
        <b>{token}</b><br><br>
        Das token kann nur einmal verwendet werden. Bitte gib dieses Token niemals weiter! Für Fragen
        wende dich gern jederzeit an <a href="mailto:admins@growv-mail.org">die Verwaltung</a>.<br><br>
        Beste Grüße und willkommen im Team!
    """
    html = BASE_HTML.replace("{content}", content)
    send(receiver, "Dein Einmaltoken", html)
