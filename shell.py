# -*- coding: utf-8 -*-

import os

from flaskext.script import Manager  # , prompt, prompt_pass, prompt_bool

from octodus import create_app
from octodus.extensions import db
from octodus.models import User
from octodus.models.model import *


manager = Manager(create_app())

from octodus import create_app
app = create_app()
project_root_path = os.path.join(os.path.dirname(app.root_path))


@manager.command
def run():
    """Run local server."""

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


@manager.command
def reset():
    """Reset database."""

    #db.reflect()
    #db.drop_all()
    db.create_all()
    user = User(username='gnufede',name='Fede', surname='Mon',
                email='gnufede@gmail.com', points=10,
                password='123456', user_type=1)

    db.session.add(user)
    db.session.commit()

manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
