

def init_subsites(app):
    from . import learning, people, banking

    learning.init_site(app)
    people.init_site(app)
    banking.init_site(app)
