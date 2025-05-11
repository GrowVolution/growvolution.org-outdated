from LIBRARY import *

SMTP_URI = "smtp.strato.de"
SMTP_PORT = 587

def _nrs():
    return SMTP(SMTP_URI, SMTP_PORT)

SENDER = "noreply@growv-mail.org"
NAME = "Team GrowVolution"
SERVICE = _nrs()
PASSWORD = ""


def _connect():
    SERVICE.starttls()
    SERVICE.login(SENDER, PASSWORD)


def _reconnect():
    global SERVICE

    SERVICE.close()
    SERVICE = _nrs()
    _connect()


def _resend(receiver, subject, html):
    _reconnect()
    send(receiver, subject, html)


def send(receiver, subject, html):
    msg = MIMEMultipart()
    msg['From'] = f"{NAME}<{SENDER}>"
    msg['To'] = receiver
    msg['Subject'] = subject
    msg['Date'] = format_datetime(datetime.now())
    msg.add_header('Reply-To', 'info@growv-mail.org')
    msg.attach(MIMEText(html, 'html'))

    try:
        SERVICE.sendmail(SENDER, receiver, msg.as_string())
    except SMTPException:
        _resend(receiver, subject, html)


def confirmation_mail(receiver, name, confirm_code):
    html = render_template('mail/confirm_email.html', user=name,
                           confirm_code=confirm_code)
    send(receiver, "E-Mail Adresse bestätigen", html)


def start(app):
    global PASSWORD
    PASSWORD = app.config["NRS_PASSWORD"]
    log('info', f"Staring mail service with SMTP server: '{SMTP_URI}:{SMTP_PORT}'")
    log('info', f"Mail service presence is '{NAME}' via '{SENDER}'.")
    _connect()
