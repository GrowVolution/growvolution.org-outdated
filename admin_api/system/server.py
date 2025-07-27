from . import SYSTEM
from ..utils import LOG_DIR


@SYSTEM.register('clear_logs')
def clear_logs():
    log_dirs = [d for d in LOG_DIR.iterdir() if d.is_dir()]
    log_dirs.append(LOG_DIR)
    for d in log_dirs:
        files = sorted([f for f in d.iterdir() if f.is_file()], key=lambda f: f.stat().st_mtime, reverse=True)
        for old_file in files[10:]:
            old_file.unlink()
