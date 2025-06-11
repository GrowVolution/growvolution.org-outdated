from cryptography.fernet import Fernet
import os, string, random, re


def randomize_username(username_raw: str) -> str:
    new_username = username_raw
    username_raw = username_raw.replace('_', '')

    for i in range(int(len(username_raw) / 7)):
        choice = random.choice(username_raw)
        new_char = random.choice(string.ascii_letters + string.digits)
        new_username = new_username.replace(choice, new_char)

    return new_username


def normalize_phone(phone: str) -> str:
    phone = re.sub(r"[^\d+]", "", phone)

    if phone.startswith("00"):
        phone = "+" + phone[2:]
    elif phone.startswith("0"):
        phone = "+49" + phone[1:]
    elif not phone.startswith("+"):
        phone = "+49" + phone

    return phone


def get_fernet():
    key = os.getenv('TWOFA_KEY')
    return Fernet(key)


def fernet_encrypted(data: bytes) -> str:
    return get_fernet().encrypt(data).decode()


def fernet_decrypted(data: bytes) -> str:
    return get_fernet().decrypt(data).decode()
