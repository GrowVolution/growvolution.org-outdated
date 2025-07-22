

def init_socket():
    from .events import init_events
    from .messages import init_messages
    init_events()
    init_messages()
