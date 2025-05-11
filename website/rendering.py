from LIBRARY import render_template


def render(template, **kwargs):
    return render_template(template, **kwargs)


def render_404():
    return render('404.html'), 404


def render_error(error_id):
    return render('error.html', error_id=error_id), 500