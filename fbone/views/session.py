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
    sessions = Session.query.all()
    return render_template('session_index.html', sessions=sessions, current_user=current_user)

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
            if form.id.data and form.id.data != '':
                session = Session.query.filter_by(id=form.id.data).first()
            else:
                session = Session()
            session.begin = datetime.datetime(date.year, date.month, date.day, time_begin.hour, time_begin.minute)
            session.end = datetime.datetime(date.year, date.month, date.day, time_end.hour, time_end.minute)
            session.block_duration = form.block_duration.data
            session.block_capacity = form.block_capacity.data
            db.session.add(session)
        db.session.commit()
        return redirect(url_for('session.index'))
    return render_template('session_new.html', form=form,
                           current_user=current_user)

@session.route('/<id>')
@login_required #FIXME!!!
@admin_required
def pub(id):
    session = Session.query.filter_by(id=id).first_or_404()
    form = EditSessionForm(next=request.args.get('next'))
    form.start_date.data = session.begin
    form.end_date.data = session.end
    form.time_begin.data = session.begin.isoformat().split('T')[1]
    form.time_end.data = session.end.isoformat().split('T')[1]
    form.block_capacity.data = session.block_capacity
    form.block_duration.data = session.block_duration
    today_str = str(session.begin.year) +"-"+ str(session.begin.month) + "-" + str(session.begin.day)
    form.id.data = session.id
    return render_template('session_new.html', form=form, today=today_str, current_user=current_user, duration=form.block_duration.data, capacity=form.block_capacity.data)

@session.route('/view/del/<id>')
@login_required 
@admin_required
def delete(id):
    appointment_user= request.args.get("user_id", None)
    appointment_project = request.args.get("project_id", None)
    session = Session.query.filter_by(id=id).first_or_404()
    if appointment_user:
        appointment = Appointment.query.filter_by(session_id=session.id, user_id=appointment_user, project_id=appointment_project).first()
        db.session.delete(appointment)
        db.session.commit()
    return redirect(url_for('session.view',session.id))

@session.route('/del/<id>')
@login_required 
@admin_required
def delete(id):
    session = Session.query.filter_by(id=id).first_or_404()
    db.session.delete(session)
    db.session.commit()
    return redirect(url_for('session.index'))

@session.route('/view/<id>')
@login_required 
@admin_required
def view(id):
    session = Session.query.filter_by(id=id).first_or_404()
    appointments = db.session.query(Appointment.date, Project.activation_key, User.name, User.surname, User.email, Appointment.session_id, Appointment.user_id, Appointment.project_id).\
            filter(session.id == Appointment.session_id).\
            filter(User.id == Appointment.user_id).\
            filter(Project.id == Appointment.project_id).\
            order_by(Appointment.date).\
            all()
           # filter(Session.id == session.id, ).\
    #users = User.query.filter_by()
    return render_template('list.html', objects=appointments, title="Citas para el "+session.begin.date().isoformat(), delete=[('session_id',-3), ('user_id',-2), ('project_id',-1)] , fields=['date', 'name', 'surname', 'email', 'activation_key' ])
