import string, random


def random_code(length: int = 6) -> str:
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
