from .. import SOCKET
from ..api import API, deny
from shared.debugger import log
from shared.utils import random_code

from flask import request
import sys, traceback


@SOCKET.on('connect')
def on_connect():
    sid = request.sid
    ip = request.remote_addr
    agent = request.headers.get('User-Agent')
    agent = agent if agent else 'no-agent'
    log('socket', f"New connection from {ip:15} via ({agent}) - Socket ID: {sid}")


@SOCKET.on('default_event')
def default_event(data: dict):
    event = data['event']
    payload = data.get('payload')
    sid = request.sid
    log('event', f"'{event}' called by {sid}.")

    ident = data.get('ident')
    if not ident:
        deny("Missing identification data.")

    process = API.resolve('process_request')
    return process(ident, event, payload)


@SOCKET.on_error_default
def error_handler(error):
    eid = random_code()
    tb_str = ''.join(traceback.format_exception(*sys.exc_info()))
    name = type(error).__name__
    log('error', f"Handling socket event failed ({eid}): {name}\n{tb_str}")

    return {'error': f"Server error while handling request ({eid})."}
