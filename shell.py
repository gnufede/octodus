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
    user = User(name='Perico', surname='De los Palotes', email='tester@hz.com', password='123456', type=1)
    proceso = Proceso(content="<div> <p> hola </p> </div>")

    group = Group(name='Universidad de Vicalvaro', activation_key='VICALVARO', depth=0, type='Universidad')
    group1 = Group(name='Ingenieria Informatica', activation_key='INFOR', depth=1, type='Titulacion')
    group2 = Group(name='Especialista en HW', activation_key='HW', depth=2, type='Especialidad')
    group3 = Group(name='Especialista en SW', activation_key='SW', depth=2, type='Especialidad')
    group4 = Group(name='Tarde', activation_key='T', depth=3, type='Grupo')

    group.children.append(group1)
    group1.children.append(group2)
    group1.children.append(group3)
    group2.children.append(group4)

    project = Project(term="2012")
    project.nodes.append(group)
    db.session.commit()
    user.projects.append(project)

    db.session.add(user)
    db.session.add(proceso)
#    project.create() 
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
