from pathlib import Path
from flask import Response, redirect
import random, string

ROOT_PATH = Path(__file__).parent

POST_METHOD = ['POST']
ALL_METHODS = ['GET', 'POST']


def back_home() -> Response:
    return redirect('/')


def back_to_login() -> Response:
    return redirect('/login')


def random_code(length: int = 6) -> str:
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
