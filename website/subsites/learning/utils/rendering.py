from website.utils.rendering import render as main_render


def render(template: str, **kwargs) -> str:
    return main_render(f"subsites/learning/{template}", **kwargs)


def render_404():
    return render('404.html'), 404


def render_error(error_id: str):
    return render('error.html', error_id=error_id), 500
