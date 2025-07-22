import eventlet
eventlet.monkey_patch()

from website import APP, init_app

init_app()

app = APP