# -*- coding: utf-8 -*-

import os

from flaskext.script import Manager, prompt, prompt_pass, prompt_bool

from fbone import create_app
from fbone.extensions import db
from fbone.models import User, Group, Proceso
from fbone.models.model import *


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
    user = User(name='Jose Manuel', surname='Lopez', email='efdigitalorlas.test@gmail.com', password='123456', type=1)
    proceso = Proceso(content="<div> <p> Aqui se describe el <b>proceso</b> para hacerse la orla: </p> <ol> <li> Darse de alta.</li> <li> Completar datos personales.</li> <li> Elegir fecha para te hagamos la foto</li> <li> Elegir lote de fotos</li> <li> Votar los profesores que quieres que aparezcan</li> </ol> </div>")

    group = Group(name='Universidad de Vicalvaro', activation_key = "VICALVARO",depth=0, type='Universidad')


    db.session.add(user)
    db.session.add(proceso)
    db.session.add(group)
    db.session.commit()
    #while node.parent:
    #   print node.parent
    #   node = node.parent



manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
