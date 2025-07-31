from . import SYSTEM
from ..utils import UTILS

from threading import Thread
import os, time


@SYSTEM.register('deploy_update')
def update_project():
    merge_branches = UTILS.resolve('merge_branches')
    merge_branches()

    def restart_self():
        time.sleep(3)
        os.system("systemctl restart admin-api")

    Thread(target=restart_self, daemon=True).start()
