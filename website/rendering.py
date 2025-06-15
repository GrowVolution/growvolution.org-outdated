from .logic.auth.verification import get_user, is_admin
from .data import commit
from flask import render_template


def render(template: str, **kwargs) -> str:
    user = get_user()
    signed_in = user is not None
    current_template = template.removesuffix('.html')

    def inner_render(**optional):
        return render_template(template, template=current_template, **optional, **kwargs)

    if signed_in:
        reflection_shown = user.reflection_shown
        if not reflection_shown:
            user.reflection_shown = True
            commit()

        return inner_render(signed_in=signed_in, is_admin=is_admin(), initial_reflection=not user.reflection_done,
                            reflection_shown=reflection_shown, journey_started=user.journey_started)

    return inner_render()


def render_404():
    return render('404.html'), 404


def render_error(error_id: str):
    return render('error.html', error_id=error_id), 500
