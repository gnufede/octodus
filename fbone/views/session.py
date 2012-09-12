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


def list(sessions, actions=None):
    sessions2 = sessions[:]
    if not actions:
        actions = [['Editar', "edit", 'icon-pencil'], ['Asignar a Proyectos', "set", 'icon-hand-right'], ['Ver citas', "view", 'icon-eye-open'], ['Borrar',"del",'icon-trash']]
    for session in sessions2:
        session.citas = len(session.appointments)
        session.fecha_de_sesion = session.begin.date().isoformat()
        session.inicio = session.begin.isoformat().split('T')[1].split('.')[0]
        session.fin = session.end.isoformat().split('T')[1].split('.')[0]
    return render_template('session_index.html', sessions=sessions2, fields=['id', 'fecha_de_sesion', 'inicio', 'fin', 'block_capacity', 'block_duration', 'citas'], actions=actions ,current_user=current_user)

@session.route('/')
@login_required
def index():
    sessions = Session.query.order_by(Session.begin).all()
    return list(sessions)

@session.route('/list/<project_id>')
@login_required
def list_project(project_id):
    project = db.session.query(Project).filter(Project.id==project_id).first()
    sessions = project.sessions
    actions = [['Quitar del proyecto',"del/"+project_id+'/session','icon-trash']]
    return list(sessions,actions)

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

        dates = [date for date in (begin_date + datetime.timedelta(days) for days in range((end_date - begin_date).days + 1)) if calendar.weekday(date.year, date.month, date.day) <= friday_weekday]
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

@session.route('/edit/<id>')
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

@session.route('/view/del/<session_id>')
@login_required 
@admin_required
def delete_appointment(session_id):
    user_id = request.args.get("user_id", None)
    project_id = request.args.get("project_id", None)
    if session_id and user_id and project_id:
        Appointment.query.filter_by(session_id=session_id, user_id=user_id, project_id=project_id).delete()
        db.session.commit() # No hace falta, lo hace solo
    return redirect('session/view/'+str(session_id))

@session.route('/set/<id>')
@session.route('/list/set/<id>')
@login_required 
@admin_required
def set(id):
    return redirect("admin/session/set/"+id)

@session.route('/list/del/<project_id>/session/<id>')
@session.route('/del/<project_id>/session/<id>')
@login_required 
@admin_required
def remove_from_project(project_id, id):
    project = Project.query.filter_by(id=project_id).first()
    session = Session.query.filter_by(id=id).first()
    project.sessions.remove(session)
    db.session.commit()
    return redirect('session/list/'+str(project_id))

@session.route('/del/<id>')
@login_required 
@admin_required
def delete(id):
    session = Session.query.filter_by(id=id).first_or_404()
    db.session.delete(session)
    db.session.commit()
    return redirect(url_for('session.index'))

#@session.route('/list/view/<id>')
#@login_required 
#@admin_required
#def list_view(id):
#    return redirect("session/view/"+id)

@session.route('/view/<id>')
@session.route('/list/view/<id>')
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
