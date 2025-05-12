from LIBRARY import *

APP_CACHE = {}

DEFAULT_FUNC = lambda timestamp, duration: datetime.now() - timestamp < timedelta(minutes=duration)
COMPARING_MAP = {
    "seconds": lambda timestamp, duration: datetime.now() - timestamp < timedelta(seconds=duration),
    "minutes": DEFAULT_FUNC,
    "hours": lambda timestamp, duration: datetime.now() - timestamp < timedelta(hours=duration),
    "days": lambda timestamp, duration: datetime.now() - timestamp < timedelta(days=duration)
}


def _timestamp_valid(timestamp: datetime, valid_for: int, duration_type: str = 'minutes') -> bool:
    comparing_func = COMPARING_MAP.get(duration_type, DEFAULT_FUNC)
    return comparing_func(timestamp, valid_for)


def update_cache():
    expired_entries = [
        key for key, entry in APP_CACHE.items()
        if not _timestamp_valid(entry.get('timestamp'),
                                entry.get('valid_for'),
                                entry.get('duration_type'))
    ]
    for key in expired_entries:
        APP_CACHE.pop(key)


def add_entry(data: Any, valid_for: int, duration_type: str = 'minutes') -> str:
    """
    :param data: Any data which can be stored into a dict.
    :param valid_for: Duration for which the entry will be valid.
    :param duration_type: Can be 'seconds', 'minutes', 'hours' or 'days'; defaults to 'minutes'.
    :return: ID of the cache entry.
    """
    entry_id = random_code()
    APP_CACHE[entry_id] = {
        "timestamp": datetime.now(),
        "valid_for": valid_for,
        "duration_type": duration_type,
        "data": data
    }
    return entry_id


def request_entry_data(entry_id: str) -> Any:
    entry = APP_CACHE.get(entry_id)
    if not entry:
        return None
    if not _timestamp_valid(entry["timestamp"], entry["valid_for"], entry["duration_type"]):
        return None
    return entry["data"]


def pop_entry(entry_id: str):
    APP_CACHE.pop(entry_id, None)