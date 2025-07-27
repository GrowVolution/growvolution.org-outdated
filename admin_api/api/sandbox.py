from . import API
from .. import APP
from ..data import DATABASE
from ..utils.dev_containers import start_container, stop_container
from ..utils.sandbox_control import create_debug_process, stop_debug_process
from shared.data import add_model, delete_model


@API.register('sandbox_status')
def status(data):
    user = data['user']

    note_db = DATABASE.resolve('dev_note')
    notes = note_db.query.all()
    notes_dict = {}
    for note in notes:
        if note == user.dev_note:
            continue
        notes_dict[note.user.name] = note.note

    group_db = DATABASE.resolve('dev_group')
    groups = []
    for group in group_db.query.all():
        if group.production:
            continue
        groups.append(group.name)

    return {
        'container_status': bool(user.dev_note),
        'active_containers': len(notes),
        'notes': notes_dict,
        'dev_note': user.dev_note.note if user.dev_note else '',
        'pub_key': user.container_key or '',
        'available_groups': groups
    }


@API.register('start_sandbox')
def start_sandbox(data):
    response = { 'success': False }

    user = data['user']
    dev_note = data.get('dev_note')
    container_key = data.get('container_key')
    group = data.get('group')
    if not (dev_note and container_key and group):
        response['error'] = "Missing data"
        return response

    if container_key != user.container_key:
        user.update_container_key(container_key)

    note_db = DATABASE.resolve('dev_note')
    note = note_db(user, dev_note)
    add_model(note)

    if not APP.config['SANDBOX_MODE']:
        name = user.name
        start_container(name)
        create_debug_process(name, group)

    response['success'] = True
    return response


@API.register('stop_sandbox')
def stop_sandbox(data):
    user = data['user']
    if user.dev_note:
        delete_model(user.dev_note)

    if not APP.config['SANDBOX_MODE']:
        name = user.name
        stop_container(name)
        stop_debug_process(name)

    return { 'success': True }
