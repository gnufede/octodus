# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, g, redirect, url_for, request, flash
from flask.ext.login import login_required, current_user

from fbone.models import *
from fbone.decorators import keep_login_url
from fbone.forms import (EditDatosForm)
from fbone.extensions import db


user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/')
@login_required
def index():
    return render_template('user_index.html', current_user=current_user)

@user.route('/edit_datos', methods=['POST','GET'])
@login_required
def edit_datos(): 

    project = current_user.projects[-1]
    groups = [project,]
    while project.depth > 0:
        project = project.parent
        groups.append(project)
    groups.reverse()
    #form.set_user(current_user)
    form = EditDatosForm(next=request.args.get('next'))
    form.generate_groups(groups)
    if request.method == 'POST':
        if form.nextproject:
            group = Project.query.filter_by(id=form.nextproject.data).first()
            current_user.projects = []
        #group.users.append(current_user)
            current_user.projects.append(group)
            groups = [group,]
            db.session.commit()
            if group.children:
                return redirect(url_for('user.edit_datos'))
            else:
                flash('Datos actualizados correctamente', 'success')
        return redirect(form.next.data or url_for('user.index'))

    return render_template('user_edit_datos.html', form=form,
                           current_user=current_user, groups=groups)



@user.route('/<name>')
def pub(name):
    if current_user.is_authenticated() and current_user.name == name:
        return redirect(url_for('user.index'))

    user = User.query.filter_by(name=name).first_or_404()
    return render_template('user_pub.html', user=user)
