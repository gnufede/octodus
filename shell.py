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
    group1 = Group(name='Ingenieria Informatica', activation_key = "INFOR",depth=1, type='Titulacion')
    group2 = Group(name='Especialista en HW', activation_key = "HW", depth=2, type='Especialidad')
    group3 = Group(name='Especialista en SW', activation_key = "SW", depth=2, type='Especialidad')
    group4 = Group(name='Tarde', activation_key = "TARDE", depth=3, type='Grupo')

    group5 = Group(name='Universidad Complutense de Madrid', activation_key = "UCM",depth=0, type='Universidad')
    group6 = Group(name='Periodismo', activation_key = "PERIODISMO",depth=1, type='Titulacion')

    group7 = Group(name='Derecho', activation_key = "DERECHO",depth=1, type='Titulacion')
    group.children.append(group1)
    group.children.append(group7)
    group1.children.append(group2)
    group1.children.append(group3)
    group2.children.append(group4)
    group5.children.append(group6)

    project = Project(term="2012")

    db.session.add(user)
    db.session.add(proceso)
    db.session.add(group)
    db.session.add(group5)
    project.create(group) 
    project.create(group5) 
    db.session.commit()
    user.projects.append(project)
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
