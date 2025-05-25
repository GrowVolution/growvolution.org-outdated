from datetime import datetime
from email.mime.text import MIMEText
from email.utils import format_datetime
from smtplib import SMTP, SMTPException
from email.mime.multipart import MIMEMultipart
from flask import render_template, Flask
from debugger import log

SMTP_URI = "smtp.strato.de"
SMTP_PORT = 587

def _noreply_service() -> SMTP:
    return SMTP(SMTP_URI, SMTP_PORT)

SENDER = "noreply@growv-mail.org"
NAME = "Team GrowVolution"
SERVICE = _noreply_service()
PASSWORD = ""


def _connect():
    SERVICE.starttls()
    SERVICE.login(SENDER, PASSWORD)


def _reconnect():
    global SERVICE

    SERVICE.close()
    SERVICE = _noreply_service()
    _connect()


def _resend(receiver, subject, html):
    _reconnect()
    send(receiver, subject, html)


def send(receiver: str, subject: str, html: str):
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


def confirmation_mail(receiver: str, name: str, confirm_code: str):
    html = render_template('mail/confirm_mail.html', user=name,
                           confirm_code=confirm_code)
    send(receiver, "E-Mail Adresse bestätigen", html)


def reset_mail(receiver: str, name: str, reset_code: str):
    html = render_template('mail/reset_mail.html', user=name, reset_code=reset_code)
    send(receiver, "Passwort zurücksetzen", html)


def start(app: Flask):
    global PASSWORD
    PASSWORD = app.config["NRS_PASSWORD"]
    log('info', f"Staring mail service with SMTP server: '{SMTP_URI}:{SMTP_PORT}'")
    log('info', f"Mail service presence is '{NAME}' via '{SENDER}'.")
    _connect()
