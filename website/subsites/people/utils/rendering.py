from website import DEBUG
from flask import render_template


def render(template: str, **kwargs) -> str:
    current_template = template.removesuffix('.html')

    context = {}
    if DEBUG:
        from .processing import context_processor
        context = context_processor()

    return render_template(f"people/{template}", template=current_template, **context, **kwargs)


def render_404():
    return render('404.html'), 404


def render_error(error_id: str):
    return render('error.html', error_id=error_id), 500
