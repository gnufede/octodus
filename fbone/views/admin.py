# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, g, redirect, url_for, request, flash, jsonify
from flask.ext.login import login_required, current_user
from fbone.forms import NewGroupForm
from fbone.extensions import db

from fbone.models import User, Group
from fbone.decorators import keep_login_url, admin_required


admin = Blueprint('admin', __name__, url_prefix='/admin')

    
@admin.route('/new_group/', methods=['GET', 'POST'])
@login_required
@admin_required
def new_group():
    types = db.session.query(Group.type).filter_by(depth=0).distinct()
    node = None
    form = NewGroupForm(request.form)
    form.set_types(types)
    if 'uni' in request.values:
        node = request.values['uni']
        node = Group.query.filter_by(id=node).first()
        form.set_node(node)
    if form.validate_on_submit():
        name = form.name.data
        activation_key = form.activation_key.data
        if not form.type.data or form.type.data == "":
            type = form.choosetype.data
        else:
            type = form.type.data
        if not node:
            node = Group(name=name, activation_key = activation_key,depth=0, type=type)
            db.session.add(node)
        else:
            node.name = name
            node.activation_key = activation_key
            node.type = type
        
        db.session.commit()
        flash('Datos actualizados correctamente', 'success')
        return redirect(form.next.data or url_for('admin.index'))

    return render_template('admin_new_group.html', form=form,
                           current_user=current_user, node=node)



@admin.route('/groups/', methods=['GET'])
@login_required
@admin_required
def groups():
    if 'parent' in request.values:
        node = request.values['parent']
        node = Group.query.filter_by(id=node).first()
        nodes = db.session.query(Group.id,Group.name).filter_by(parent=node).all()
        
    else:
        nodes = db.session.query(Group.id,Group.name).filter_by(depth=0).all()
    return jsonify(nodes)


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
