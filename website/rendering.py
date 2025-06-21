from .logic.auth.verification import get_user
from .data import commit
from flask import render_template


def render(template: str, user = None, **kwargs) -> str:
    current_template = template.removesuffix('.html')

    def inner_render(**optional):
        return render_template(template, template=current_template, **optional, **kwargs)

    if not user:
        user = get_user()

    if user:
        reflection_shown = user.reflection_shown
        if not reflection_shown:
            user.reflection_shown = True
            commit()

        return inner_render(user=user)

    return inner_render()


def render_404():
    return render('404.html'), 404


def render_error(error_id: str):
    return render('error.html', error_id=error_id), 500
