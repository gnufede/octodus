# -*- coding: utf-8 -*-

import os

from flaskext.script import Manager, prompt, prompt_pass, prompt_bool

from fbone import create_app
from fbone.extensions import db
from fbone.models import User, Group, UsersGroups


manager = Manager(create_app())

from fbone import create_app
app = create_app()
project_root_path = os.path.join(os.path.dirname(app.root_path))


@manager.command
def run():
    """Run local server."""

    app.run()


@manager.command
def reset():
    """Reset database."""

    db.drop_all()
    db.create_all()
    user = User(name='tester', email='tester@hz.com', password='123456')
    rel = UsersGroups(extra_data="2012")
    rel.group = Group(name='group1', activation_key='HOLA')
    user.groups.append(rel)

    db.session.add(user)
    db.session.commit()


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
