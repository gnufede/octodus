# -*- coding: utf-8 -*-

import os

from flaskext.script import Manager, prompt, prompt_pass, prompt_bool

from fbone import create_app
from fbone.extensions import db
from fbone.models import User, Group, Proceso


manager = Manager(create_app())

from fbone import create_app
app = create_app()
project_root_path = os.path.join(os.path.dirname(app.root_path))


@manager.command
def run():
    """Run local server."""

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',port=port)


@manager.command
def reset():
    """Reset database."""

    db.drop_all()
    db.create_all()
    user = User(name='Perico', surname='De los Palotes', email='tester@hz.com', password='123456', type=1)
    proceso = Proceso(content="<div> <p> hola </p> </div>")

    #rel.group = Group(name='group1', activation_key='HOLA')
    #user.groups.append(rel)

    db.session.add(user)
    db.session.add(proceso)
    db.session.commit()


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
