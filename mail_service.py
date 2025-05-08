from LIBRARY import *

def _nrs():
    return SMTP("smtp.strato.de", 587)

SENDER = "noreply@growv-mail.org"
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


def _get_code():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))


def _get_html(content):
    return f"""
    <html>
        <body>
            <p>
                {content}
            </p>
        </body>
    </html>
    """


def _resend(receiver, subject, body, c_type):
    _reconnect()
    send(receiver, subject, body, c_type)


def send(receiver, subject, body, c_type):
    msg = MIMEMultipart()
    msg['From'] = f"GrowV Service<{SENDER}>"
    msg['To'] = receiver
    msg['Subject'] = subject
    msg['Date'] = format_datetime(datetime.now())
    msg.add_header('Reply-To', 'info@growv-mail.org')
    msg.attach(MIMEText(body, c_type))

    try:
        SERVICE.sendmail(SENDER, receiver, msg.as_string())
    except SMTPException:
        _resend(receiver, subject, body, c_type)


def start(app):
    global PASSWORD
    PASSWORD = app.config["NRS_PASSWORD"]
    _connect()
