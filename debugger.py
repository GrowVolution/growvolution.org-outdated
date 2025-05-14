from datetime import datetime

def get_time() -> str:
    offset = datetime.now().astimezone().utcoffset()
    hours = int(offset.total_seconds() // 3600)
    minutes = int((offset.total_seconds() % 3600) // 60)

    sign = '+' if offset.total_seconds() >= 0 else '-'
    offset_str = f"{sign}{abs(hours):02d}{abs(minutes):02d}"

    return f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {offset_str}"


def log(category: str, message: str):
    log_str = f"[{get_time()}] [FLASK]  [{category.upper()}] {message}"
    print(log_str)


def debug_msg(message: str):
    log('debug', message)


def start_session():
    import os
    log('info', "Logging started.")
    log('info', f"Current server instance: {os.getenv('INSTANCE')}")