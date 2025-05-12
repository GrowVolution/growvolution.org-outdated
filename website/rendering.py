from requests.models import Response

from LIBRARY import render_template
from .logic.auth.verification import authenticated_user_request


def render(template: str, **kwargs) -> str:
    return render_template(template, signed_in=authenticated_user_request(), **kwargs)


def render_404():
    return render('404.html'), 404


def render_error(error_id: str):
    return render('error.html', error_id=error_id), 500
