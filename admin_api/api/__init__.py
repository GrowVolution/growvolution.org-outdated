from .. import SOCKET
from ..data.admins import Admin
from shared.packaging import Package
from shared.debugger import log
from pathlib import Path
from datetime import datetime, UTC, timedelta
from flask import request

API = Package(Path(__file__).parent)


def emit(event: str, data: str | dict | None, **kwargs):
    SOCKET.emit(event, data, to=request.sid, **kwargs)


def no_handler(data):
    log('warn', "Event handler not found...")
    return {'error', "Unknown event!"}


def deny(reason: str):
    log('warn', f"Action aborted: {reason}")
    return {'error': f"Request denied: {reason}"}


@API.register('process_request')
def process(ident: dict, target: str, data: dict):
    auth = ident.get('auth')
    auth_type = ident.get('type')

    try:
        handler = API.resolve(target)
    except ValueError:
        handler = no_handler

    match auth_type:
        case 'default':
            user = Admin.query.filter_by(name=auth).first()
            if not user:
                return deny("Invalid authentication data.")

            signature = ident.get('signature')
            if not (signature and user.verify_signature(data, signature)):
                 return deny("Invalid signature.")

            timestamp_str = data.get('timestamp')
            timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
            if not timestamp or datetime.now(UTC) - timestamp > timedelta(minutes=1):
                return deny("Invalid timestamp.")

            return handler(data)

        case 'token':
            data['token'] = ident.get('token')
            return handler(data)

        case _:
            return deny("Invalid authentication type.")
