from shared.debugger import log
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import format_datetime
from smtplib import SMTP, SMTPException
from email.mime.multipart import MIMEMultipart
from flask import Flask

SMTP_URI = "smtp.strato.de"
SMTP_PORT = 587

def _smtp_service() -> SMTP:
    return SMTP(SMTP_URI, SMTP_PORT)

SENDER = "noreply@growv-mail.org"
REPLY_TO = "info@growv-mail.org"
NAME = "Team GrowVolution"
SERVICE = _smtp_service()
PASSWORD = ""


def _connect():
    SERVICE.starttls()
    SERVICE.login(SENDER, PASSWORD)


def _reconnect():
    global SERVICE

    SERVICE.close()
    SERVICE = _smtp_service()
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
    msg.add_header('Reply-To', '')
    msg.attach(MIMEText(html, 'html'))

    try:
        SERVICE.sendmail(SENDER, receiver, msg.as_string())
    except SMTPException:
        _resend(receiver, subject, html)


def start(app: Flask, is_admin: bool = False):
    global PASSWORD, REPLY_TO, NAME
    PASSWORD = app.config["NRS_PASSWORD"]
    REPLY_TO = "admins@growv-mail.org" if is_admin else REPLY_TO
    NAME = "Administration @ GrowVolution" if is_admin else NAME
    log('info', f"Staring mail service with SMTP server: '{SMTP_URI}:{SMTP_PORT}'")
    log('info', f"Mail service presence is '{NAME}' via '{SENDER}'.")
    _connect()
