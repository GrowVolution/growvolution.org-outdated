from LIBRARY import *

SOCKET = SocketIO(async_mode='eventlet')
HANDLERS = {}


def register_event(name):
    def decorator(handler):
        HANDLERS[name] = handler
        return handler
    return decorator


def no_handler(data):
    log('warn', "Event handler not found...")
    SOCKET.emit('error', "Unknown event!")