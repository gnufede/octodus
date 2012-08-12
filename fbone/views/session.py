# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, g, redirect, url_for, request
from flask.ext.login import login_required, current_user

from fbone.models import *
from fbone.decorators import keep_login_url, admin_required
from fbone.forms import (EditSessionForm)
from fbone.extensions import db

import datetime

session = Blueprint('session', __name__, url_prefix='/session')


@session.route('/')
@login_required
def index():
    return render_template('user_index.html', current_user=current_user)

@session.route('/nueva_sesion')
@login_required
@admin_required
def new_session():
    form = EditSessionForm(next=request.args.get('next'))
    #form.set_user(current_user)
    return render_template('session_new.html', form=form,
                           current_user=current_user)

@session.route('/nueva_sesion', methods=['POST'])
@login_required #FIXME!!!
@admin_required
def new_session_post():
    form = EditSessionForm(next=request.args.get('next'))
    session = Session()
    session.begin = datetime.strptime(form.begin)
    session.end = datetime.strptime(form.end)
    session.block_duration = int(form.block_duration)
    session.block_capacity = int(form.block_capacity)

@session.route('/<name>')
def pub(name):
    if current_user.is_authenticated() and current_user.name == name:
        return redirect(url_for('user.index'))

    user = User.query.filter_by(name=name).first_or_404()
    return render_template('user_pub.html', user=user)
