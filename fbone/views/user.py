# -*- coding: utf-8 -*-

import datetime

from flask import Blueprint, render_template, current_app, g, redirect, url_for, request, flash
from flask.ext.login import login_required, current_user

from fbone.models import *
from fbone.decorators import keep_login_url
from fbone.forms import (EditDatosForm, EditDateForm, UserAppointmentForm)
from fbone.extensions import db
from sqlalchemy import Date, cast
import datetime


user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/')
@login_required
def index():
    return render_template('user_index.html', current_user=current_user)

@user.route('/edit_date', methods=['POST','GET'])
@login_required
def edit_date(): 
    project = current_user.projects[-1]
    form = EditDateForm(next=request.args.get('next'))
    if request.method == 'POST':
        date = Session.query.filter_by(id=form.date.data).first()
        appointment = Appointment(project=project,user=current_user,session=date,date=date.begin)
        db.session.add(appointment)
        db.session.commit()
        return redirect(form.next.data or url_for('user.index'))

    dates = Session.query.filter( cast(Session.begin,Date) > datetime.date.today()).all()
    form.generate_dates(dates)
    return render_template('user_edit_date.html', form=form, current_user=current_user)

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



@user.route('/new_appointment', methods=['GET'])
@login_required
def new_appointment_get():
    project = current_user.projects[-1] # FIXME
    session_id = request.args.get('session_id', None)
    form = UserAppointmentForm()
    if not session_id:
        # get all sessions for this project
        sessions = [ [s.begin.date().isoformat(), int(s.id)] for s in project.sessions if s.begin > datetime.datetime.now() ]
        return render_template('user_appointment.html', form=form, sessions=sessions)
    else:
        # get all hours for this session
        sess = Session.query.filter_by(id=session_id).first()
        interval_timedelta = sess.end - sess.begin
        interval_mins = interval_timedelta.total_seconds() / 60
        all_hours = [ sess.begin + datetime.timedelta(minutes=x) for x in range(0, interval_mins, sess.block_duration) ]
        all_hours_occupation = [ (h, len([ apn for apn in sess.appointments if apn.date == h ])) for h in all_hours ]
        hours = [ (h, n) for (h, n) in all_hours_occupation if n < sess.block_capacity ]
        return render_template('user_appointment.html', form=form, hours=hours, session=sess)
        

@user.route('/new_appointment', methods=['POST'])
@login_required
def new_appointment_post():
    session_id = request.args.get('session_id', None)
    appointment_date = form.date.data
    project =current_user.projects[-1] # FIXME
    if not session_id or not appointment_date:
        # TODO
        return redirect(url_for('user.new_appointment_get'))
    previous_appointment = Appointment.query.filter_by(user=current_user, project=project).first()
    if previous_appointment:
        if previous_appointment.date < datetime.datetime.now():
            #TODO #ERROR, permitimos cambiar fecha de appointment si ya ha ocurrido?
            return redirect(form.next.data or url_for('user.index'))
        #TODO elif si la fecha de modificación de appointments ya ha ocurrido, no dejamos cambiar el appointment
        else:
            appointment = previous_appointment

    appointment = Appointment()
    appointment.date = appointment_date
    appointment.project = current_user.projects[-1] # FIXME
    appointment.user = current_user
    appointment.session = Session.query.filter_by(id=session_id).first()
    db.session.commit()

        





