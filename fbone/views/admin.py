# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, g, redirect, url_for, request, flash, jsonify
from flask.ext.login import login_required, current_user
from fbone.forms import NewGroupForm, EditProcesoForm, NewProjectForm
from fbone.extensions import db

from fbone.models import User, Group, Proceso, Project
from fbone.decorators import keep_login_url, admin_required


admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/new_project/', methods=['GET', 'POST'])
@login_required
@admin_required
def new_project():
    group = None
    project = None
    form = NewProjectForm(request.form)
    if form.validate_on_submit():
        term = form.term.data

        if form.group.data:
            group = Group.query.filter_by(id=form.group.data).first()
        project = Project.query.filter_by(id=form.project_id.data).first()
        if not form.project_id.data or form.project_id.data == '':
            project = Project.query.filter_by(term=form.term.data,name='0').first()
            if not project:
                project = Project(term=term, name='0')
                db.session.add(project)
        else:
            project = Project.query.filter_by(id=form.project_id.data).first()
            project.term = term

        if group:
            project.create(group)
        
        db.session.commit()
        flash('Datos actualizados correctamente', 'success')
        return redirect(form.next.data or url_for('admin.new_project'))

    return render_template('admin_new_project.html', form=form,
                           current_user=current_user, project=project)

@admin.route('/new_group/', methods=['GET', 'POST'])
@login_required
@admin_required
def new_group():
    depth = 0
    parent = None
    node = None
    form = NewGroupForm(request.form)
    if 'uni' in request.values:
        node = request.values['uni']
        node = Group.query.filter_by(id=node).first()
    if form.validate_on_submit():
        name = form.name.data
        activation_key = form.activation_key.data
        #if not form.type.data or form.type.data == "":
        type = form.choosetype.data
        if form.parent.data:
            parent = Group.query.filter_by(id=form.parent.data).first()
            depth = parent.depth + 1
        #else:
        #    type = form.type.data
        
        if not form.group_id.data or form.group_id.data == '':
            if parent:
                node = Group(name=name, activation_key = activation_key,depth=depth, type=type, parent_id=parent.id)
            else:
                node = Group(name=name, activation_key = activation_key,depth=depth, type=type)
            db.session.add(node)
        else:
            node = Group.query.filter_by(id=form.group_id.data).first()
            node.name = name
            node.activation_key = activation_key
            node.type = type
            node.depth = depth
            if parent:
                node.parent_id = parent.id
                node.depth = parent.depth + 1
        
        db.session.commit()
        flash('Datos actualizados correctamente', 'success')
        return redirect(form.next.data or url_for('admin.new_group'))

    return render_template('admin_new_group.html', form=form,
                           current_user=current_user, node=node)



@admin.route('/grouptypes/', methods=['GET'])
@login_required
@admin_required
def grouptypes():
    types = db.session.query(Group.type,Group.type).distinct()
    return jsonify(types)
    

@admin.route('/groups/', methods=['GET'])
@login_required
@admin_required
def groups():
    if 'parent' in request.values:
        node_id = request.values['parent']
        node = Group.query.filter_by(id=node_id).first()
        tree = db.session.query(Group.id,Group.name).filter_by(parent=node).all()
    else:
        tree = [(x.id, x.jsonify()) for x in Group.query.filter_by(depth=0)]
    return jsonify(tree)
    

@admin.route('/edit_proceso', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_proceso():
    form = EditProcesoForm(request.form)
    #if form.validate_on_submit():
    if request.method == 'POST':
        proceso = Proceso.query.first()
        proceso.content = form.textarea.data
        db.session.commit()
        return redirect(url_for('user.index'))
    proceso = Proceso.query.first()
    return render_template('edit_proceso.html', proceso=proceso.content, form=form)


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
