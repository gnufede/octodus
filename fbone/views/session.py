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
    date_today = datetime.date.today()
    today_str = str(date_today.year) +"-"+ str(date_today.month) + "-" + str(date_today.day)
    form = EditSessionForm(next=request.args.get('next'))
    #form.set_user(current_user)
    return render_template('session_new.html', form=form,
                           current_user=current_user, today=today_str, duration=10, capacity=4)

@session.route('/nueva_sesion', methods=['POST'])
@login_required #FIXME!!!
@admin_required
def new_session_post():
    form = EditSessionForm(next=request.args.get('next'))
    if form.validate_on_submit():
        session = Session()
        session.begin = form.date.data+" "+form.begin.data+":00"
        session.end = form.date.data+" "+form.end.data+":00"
        session.block_duration = form.block_duration.data
        session.block_capacity = form.block_capacity.data
        db.session.add(session)
        db.session.commit()
        return redirect(url_for('user.index'))
    return render_template('session_new.html', form=form,
                           current_user=current_user)

@session.route('/<name>')
def pub(name):
    if current_user.is_authenticated() and current_user.name == name:
        return redirect(url_for('user.index'))

    user = User.query.filter_by(name=name).first_or_404()
    return render_template('user_pub.html', user=user)
