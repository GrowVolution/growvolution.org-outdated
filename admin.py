from eventlet import monkey_patch
monkey_patch()

from admin_api import APP, init_app
init_app()

app = APP
