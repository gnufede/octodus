# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, \
                    url_for, request, flash, jsonify
                    #g, current_app
from flask.ext.login import login_required, current_user
#from octodus.forms import NewGroupForm, EditPageForm, NewProjectForm, \
#                        SetSessionForm, NewOfferForm, SetOfferForm, \
#                        NewActForm, NewPollItemForm, SetPollNodeForm, \
#                        SetPollForm
from octodus.extensions import db

from octodus.models import User, Project
from octodus.decorators import admin_required
                            #, keep_login_url
import datetime
from werkzeug import secure_filename, generate_password_hash
                    #, check_password_hash
import os
import zipfile
import shutil

admin = Blueprint('admin', __name__, url_prefix='/admin')
UPLOAD_FOLDER = '/tmp/'
admin.config = dict()
admin.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def render_projects(objects):
    for object in objects:
        object.sesiones = len(object.sessions)
        object.ofertas = len(object.offers)
        object.usuarios = len(object.users)
    return render_template('list.html', title="Proyectos", objects=objects,
        fields=["id", "activation_key", "term", "type", "name", "sesiones",
        "ofertas", "usuarios"], actions=[['Ver Sesiones', "view_session",
        'icon-camera'], ['Asignar Sesiones', "set_session", 'icon-hand-right'],
         ['Ver Ofertas', "view_offer", 'icon-shopping-cart'],
         ['Asignar Ofertas', "set_offer", 'icon-hand-right'],
         ['Borrar', "del", 'icon-trash']], active='project_list',
         current_user=current_user)



@admin.route('/project/list/<name>')
@login_required
@admin_required
def project_list_name(name):
    objects = db.session.query(Project).\
            filter(Project.name != '0', Project.term == name).all()
    return render_projects(objects)


@admin.route('/project/list')
@login_required
@admin_required
def project_list():
    objects = db.session.query(Project).filter(Project.name != '0').all()
    return render_projects(objects)



@admin.route('/')
@login_required
def index():
    return render_template('user_index.html', current_user=current_user)


@admin.route('/<name>')
def pub(name):
    if current_user.is_authenticated() and current_user.name == name:
        return redirect(url_for('user.index'))

    user = User.query.filter_by(name=name).first_or_404()
    return render_template('user_pub.html', user=user)
