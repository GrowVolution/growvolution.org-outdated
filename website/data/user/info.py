from .. import DB
from website.utils import normalize_phone
from typing import Optional
from sqlalchemy.ext.hybrid import hybrid_property

LEVEL_INFO = {
    'level_status': {
        1: 'Neuling',
        2: 'Anfänger',
        3: 'Aufgebrochen',
        4: 'Wachsender',
        5: 'Suchender',
        6: 'Gestaltender',
        7: 'Wandler',
        8: 'Mentor',
        9: 'Leuchtturm',
        10: 'Meister'
    },
    'level_icon': {
        1: 'bi-emoji-smile text-secondary',
        2: 'bi-lightbulb text-warning',
        3: 'bi-signpost text-info',
        4: 'bi-bar-chart text-success',
        5: 'bi-eye text-primary',
        6: 'bi-palette text-danger',
        7: 'bi-arrow-repeat text-info',
        8: 'bi-person-heart text-success',
        9: 'bi-sun text-warning',
        10: 'bi-gem text-purple'
    },
    'xp_threshold': {
        1: 0,
        2: 200,
        3: 1000,
        4: 2500,
        5: 5000,
        6: 10000,
        7: 17500,
        8: 27500,
        9: 42500,
        10: 67500
    }
}


def _level_status(level: int) -> str:
    return LEVEL_INFO['level_status'].get(level, 'Unbekannt')


def _level_icon(level: int) -> str:
    return LEVEL_INFO['level_icon'].get(level, 'bi-person')


def _xp_threshold(level: int, level_up: bool = True) -> int | float:
    return LEVEL_INFO['xp_threshold'].get(level, float('inf') if level_up else 0)


def _level_up(level: int, xp: int) -> bool:
    return xp >= _xp_threshold(level + 1)


def _level_down(level: int, xp: int) -> bool:
    return xp < _xp_threshold(level, False)


class UserInfo:
    birthdate = DB.Column(DB.Date)
    gender = DB.Column(DB.String(1))  # 'm', 'w', 'd'
    phone = DB.Column(DB.String(32))
    address = DB.Column(DB.String(255))  # Format: street|number|postal|city
    contact_consent = DB.Column(DB.Boolean, default=False)

    xp = DB.Column(DB.Integer, nullable=False, default=0)
    level = DB.Column(DB.Integer, nullable=False, default=1)

    @hybrid_property
    def level_status(self) -> str:
        return _level_status(self.level)

    @hybrid_property
    def next_level_status(self) -> str:
        return _level_status(self.level + 1)

    @hybrid_property

    @hybrid_property
    def level_icon(self) -> str:
        return _level_icon(self.level)

    @hybrid_property
    def score(self) -> float:
        ratio = self.xp / _xp_threshold(self.level + 1)
        return ratio * 100

    @hybrid_property
    def address_dict(self) -> Optional[dict]:
        if not self.address or "|" not in self.address:
            return None
        parts = self.address.split("|")
        if len(parts) != 4:
            return None
        return {
            "street": parts[0],
            "number": parts[1],
            "postal": parts[2],
            "city": parts[3]
        }

    @hybrid_property
    def address_str(self) -> str:
        a = self.address_dict
        return f"{a['street']} {a['number']}, {a['postal']} {a['city']}" if a else "Keine Angabe"

    def set_address(self, street: str, number: str, postal: str, city: str):
        self.address = f"{street}|{number}|{postal}|{city}"

    def set_phone(self, phone: str):
        self.phone = normalize_phone(phone)

    def add_xp(self, xp: int):
        self.xp += xp
        if _level_up(self.level, self.xp) and self.level < 10:
            self.level += 1

    def remove_xp(self, xp: int):
        self.xp = max(0, self.xp - xp)
        if _level_down(self.level, self.xp) and self.level > 1:
            self.level -= 1
