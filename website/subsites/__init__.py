

def init_subsites(app):
    from . import learning, people

    learning.init_site(app)
    people.init_site(app)
