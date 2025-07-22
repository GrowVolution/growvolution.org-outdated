

def init_models(app):
    from . import user, blog, journey, journal, dev
    from .comment_system import comment, reply

    from website.subsites.people import data as people_data
    from website.subsites.learning import data as learning_data
    from website.subsites.banking import data as banking_data

    with app.app_context():
        people_data.init_models()
        learning_data.init_models()
        banking_data.init_models()
