from .. import require_user, METHODS
from website.logic.user import journal as journal_handler
from flask import Blueprint

journal = Blueprint('journal', __name__)


@journal.route('/')
@require_user(False)
def main(user):
    return journal_handler.handle_request(user)


@journal.route('/history')
@require_user(False)
def journal_history(user):
    return journal_handler.journal_history(user)


@journal.route('/set', methods=METHODS.POST)
@require_user(True)
def set_journal(user):
    return journal_handler.set_journal(user)


@journal.route('/add-entry', methods=METHODS.POST)
@require_user(False)
def add_journal_entry(user):
    return journal_handler.add_entry(user)
