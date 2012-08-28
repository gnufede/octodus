# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, g, redirect, url_for, request
from flask.ext.login import login_required, current_user

from fbone.models import *
from fbone.decorators import keep_login_url, admin_required
from fbone.forms import (EditSessionForm)
from fbone.extensions import db

import datetime
import calendar
import dateutil.parser

session = Blueprint('session', __name__, url_prefix='/session')


@session.route('/')
@login_required
def index():
    return render_template('user_index.html', current_user=current_user)

@session.route('/nueva_sesion', methods=['GET'])
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
        friday_weekday = 4
        begin_date = dateutil.parser.parse(form.start_date.data)
        end_date = dateutil.parser.parse(form.end_date.data)
        time_begin = dateutil.parser.parse(form.time_begin.data)
        time_end = dateutil.parser.parse(form.time_end.data)

        dates = [date for date in (begin_date + datetime.timedelta(days) for days in range((end_date - begin_date).days)) if calendar.weekday(date.year, date.month, date.day) <= friday_weekday]
        if not dates:
            dates = [begin_date,]

        for date in dates:
            session = Session()
            session.begin = datetime.datetime(date.year, date.month, date.day, time_begin.hour, time_begin.minute)
            session.end = datetime.datetime(date.year, date.month, date.day, time_end.hour, time_end.minute)
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
