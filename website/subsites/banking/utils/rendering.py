from flask import render_template


def render(template: str, **kwargs) -> str:
    current_template = template.removesuffix('.html')
    return render_template(f"banking/{template}", template=current_template, **kwargs)


def render_404():
    return render('404.html'), 404


def render_error(error_id: str):
    return render('error.html', error_id=error_id), 500
