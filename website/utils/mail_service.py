from shared.mail_service import send
from flask import render_template
from datetime import datetime


def confirmation_mail(receiver: str, name: str, confirm_code: str):
    html = render_template('mail/confirm_mail.html', user=name,
                           confirm_code=confirm_code)
    send(receiver, "E-Mail Adresse bestätigen", html)


def email_change_mail(receiver: str, name: str, confirm_code: str):
    html = render_template('mail/confirm_change_mail.html', user=name,
                           confirm_code=confirm_code)
    send(receiver, "Neue E-Mail Adresse", html)


def reset_mail(receiver: str, name: str, reset_code: str):
    html = render_template('mail/reset_mail.html', user=name, reset_code=reset_code)
    send(receiver, "Passwort zurücksetzen", html)


def login_notify(receiver: str, name: str):
    html = render_template('mail/login_notification.html',
                           user=name, timestamp=datetime.now().strftime("%d.%m.%Y, %H:%M:%S Uhr"))
    send(receiver, "Login Benachrichtigung", html)
