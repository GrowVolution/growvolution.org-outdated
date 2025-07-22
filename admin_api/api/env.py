from . import API
from ..data.environment import Environment
from shared.data import add_model, commit, delete_model


@API.register('get_env')
def get_env(_):
    return { 'keys': [v.key for v in Environment.query.all()] }


@API.register('set_var')
def set_env(data):
    response = { 'success': False }
    key = data.get('key')
    value = data.get('value')
    if not (key and value):
        response['error'] = 'Missing data'
        return response

    var = Environment.query.get(key)
    if var:
        var.update_value(value)
        commit()
    else:
        var = Environment(key, value)
        add_model(var)

    response['success'] = True
    return response


@API.register('del_var')
def delete_env(data):
    response = { 'success': False }
    key = data.get('key')
    if not key:
        response['error'] = 'Missing data'
        return response

    var = Environment.query.get(key)
    if var:
        delete_model(var)

    response['success'] = True
    return response
