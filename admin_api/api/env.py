from . import API
from ..data import DATABASE
from shared.data import add_model, commit, delete_model


@API.register('get_env')
def get_env(_):
    env = DATABASE.resolve('env')
    return { 'keys': [v.key for v in env.query.all()] }


@API.register('get_groups')
def get_groups(data):
    key = data.get('key')
    var = None
    if key:
        env = DATABASE.resolve('env')
        var = env.query.get(key)

    groups = {}
    group_db = DATABASE.resolve('env_group')
    for group in group_db.query.all():
        checked = var in group.vars if var else False
        groups[group.name] = checked

    return { 'groups': groups }


@API.register('set_var')
def set_env(data):
    response = { 'success': False }

    key = data.get('key')
    value = data.get('value')
    group_names = set(data.get('groups') or [])

    if not key or (value is None and not group_names):
        response['error'] = 'Missing data'
        return response

    env_model = DATABASE.resolve('env')
    group_model = DATABASE.resolve('env_group')

    var = env_model.query.get(key)

    if value:
        if var:
            var.update_value(value)
        else:
            var = env_model(key, value)
            add_model(var)
    elif not var:
        response['error'] = 'New vars cannot have empty values'
        return response

    if group_names:
        for group in group_model.query.all():
            selected = group.name in group_names
            contains = var in group.vars

            if selected and not contains:
                group.add_var(var)
                group_names.remove(group.name)
            elif not selected and contains:
                group.pop_var(var)

        for name in group_names:
            new_group = group_model(name)
            new_group.add_var(var)
            add_model(new_group)

    commit()
    response['success'] = True
    return response


@API.register('del_var')
def delete_env(data):
    response = { 'success': False }
    key = data.get('key')
    if not key:
        response['error'] = 'Missing data'
        return response

    env = DATABASE.resolve('env')
    var = env.query.get(key)
    if var:
        delete_model(var)

    response['success'] = True
    return response
