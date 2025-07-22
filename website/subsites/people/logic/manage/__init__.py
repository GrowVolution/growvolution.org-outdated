from ...utils.rendering import render


def handle_request(user):
    kwargs = {}

    if user.has_permissions(['view_roles', 'manage_roles']):
        pass

    return render('manage/dashboard.html')