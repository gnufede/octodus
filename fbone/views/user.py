# -*- coding: utf-8 -*-

import datetime

from flask import Blueprint, render_template, current_app, g, redirect, url_for, request, flash
from flask.ext.login import login_required, current_user

from fbone.models import *
from fbone.decorators import keep_login_url, admin_required
from fbone.forms import (EditDatosForm, UserAppointmentForm, UserOfferForm)
from fbone.extensions import db
from sqlalchemy import Date, cast
import datetime


user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/')
@login_required
def index():
    return render_template('user_index.html', current_user=current_user)

@user.route('/ayuda')
@login_required
def ayuda():
    return render_template('user_email.html', current_user=current_user)

@user.route('/edit_date', methods=['POST','GET'])
@login_required
def edit_date(): 
    project = current_user.projects[-1]
    form = EditDateForm(next=request.args.get('next'))
    if request.method == 'post':
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
    commit = False
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
        if form.incorrect.data:
            return redirect(url_for('user.ayuda'))
        if form.name.data != current_user.name:
            current_user.name = form.name.data
            commit = True
        if form.surname.data != current_user.surname:
            current_user.surname = form.surname.data
            commit = True
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
        if commit:
            db.session.commit()
            flash('Datos actualizados correctamente', 'success')
        return redirect(form.next.data or url_for('user.index'))

    return render_template('user_edit_datos.html', form=form,
                           current_user=current_user, groups=groups)


@user.route('/list')
@login_required
@admin_required
def list():
    users2 = User.query.all()
    users = users2[:]
    for user in users:
        if user.appointments:
            user.cita = user.appointments[0].date
        else:
            user.cita = ''
    return render_template('list.html', title="Usuarios", objects=users, fields=['name', 'surname', 'email', 'cita'],no_set_delete=True,  active='user_list', current_user=current_user)

@user.route('/<name>')
def pub(name):
    if current_user.is_authenticated() and current_user.name == name:
        return redirect(url_for('user.index'))

    user = User.query.filter_by(name=name).first_or_404()
    return render_template('user_pub.html', user=user)

@user.route('/del/<id>')
@login_required 
@admin_required
def delete(id):
    user = User.query.filter_by(id=id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user.list'))


@user.route('/new_appointment', methods=['GET'])
@login_required
def new_appointment_get():
    project = current_user.projects[-1] # FIXME
    session_id = request.args.get('session_id', None)
    form = UserAppointmentForm()
    if not session_id:
        # get all sessions for this project
        sessions = [ [s.begin.date().isoformat(), int(s.id)] for s in project.sessions if s.begin > datetime.datetime.now() ]
        sessions=sorted(sessions)
        return render_template('user_appointment.html', form=form, sessions=sessions)
    else:
        # get all hours for this session
        sess = Session.query.filter_by(id=session_id).first()
        interval_timedelta = sess.end - sess.begin
        #hack so it works in python2.6
        td = interval_timedelta
        total_seconds = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
        interval_mins = int(total_seconds / 60) 
                        #int(interval_timedelta.total_seconds() / 60)
        all_hours = [ sess.begin + datetime.timedelta(minutes=x) for x in range(0, interval_mins, sess.block_duration) ]
        all_hours_occupation = [ (h, len([ apn for apn in sess.appointments if apn.date == h ])) for h in all_hours ]
        #hours = [ (h, n) for (h, n) in all_hours_occupation if n < sess.block_capacity ]
        hours = [ (h, str(h).split()[1])  for (h, n) in all_hours_occupation if n < sess.block_capacity ]
        form.set_hours(hours)
        form.session.data = session_id
        return render_template('user_appointment.html', form=form, hours=hours, session=sess)
        

@user.route('/new_appointment', methods=['POST'])
@login_required
def new_appointment_post():
    #session_id = request.args.get('session_id', None)
    form = UserAppointmentForm()
    session_id = form.session.data
    appointment_date = form.hour.data
    project =current_user.projects[-1] # FIXME
    if not session_id or not appointment_date:
        # TODO
        flash(u'Datos actualizados incorrectamente', 'error')
        return redirect(url_for('user.new_appointment_get'))
    
    # Count appointments in this slot
    count = Appointment.query.filter_by(session_id=session_id, project_id=project.id, date=appointment_date).count()
    sess = Session.query.filter_by(id=session_id).first()
    if count >= sess.block_capacity:
        flash(u"La hora elegida ya se ha completado", 'error')
        return redirect(url_for('user.new_appointment_get'))
        #return redirect(form.next.data or url_for('user.index'))
    
    previous_appointment = Appointment.query.filter_by(user=current_user, project=project).first()
    if previous_appointment:
        if previous_appointment.date < datetime.datetime.now():
            flash('Lo sentimos, su cita ya ha tenido lugar', 'error')
            #TODO #ERROR, permitimos cambiar fecha de appointment si ya ha ocurrido?
            return redirect(form.next.data or url_for('user.index'))
        #TODO elif si la fecha de modificación de appointments ya ha ocurrido, no dejamos cambiar el appointment
        else:
            appointment = previous_appointment
    else:
        appointment = Appointment()
    appointment.date = appointment_date
    appointment.project = current_user.projects[-1] # FIXME
    appointment.user = current_user
    appointment.session = Session.query.filter_by(id=session_id).first()
    db.session.commit()
    time = appointment_date.split()[1]
    (year, month, day) = appointment_date.split()[0].split('-')
    flash('Cita confirmada correctamente para el '+day+'-'+month+'-'+year+' a las '+time+')', 'success')
    return redirect(form.next.data or url_for('user.index'))

@user.route('/set_offer/<type_id>', methods=['GET', 'POST'])
@user.route('/set_offer/', methods=['GET', 'POST'])
@login_required
def set_offer(type_id=1):
    form = UserOfferForm()
    form.set_offer_type(type_id)
    project = current_user.projects[-1] #FIXME
    
    if len(current_user.offer_selection):
        for selection in current_user.offer_selection:
            db.session.delete(selection)
        db.session.commit()

    if request.method == 'POST':
        next_offer = Offer.query.filter_by(type=str(int(type_id)+1)).first()
        if form.options.data != u'None':
            offer = Offer.query.get(int(form.options.data))
            offer_selection = OfferSelection(offer_id=offer.id, project_id=project.id, user_id=current_user.id, offer_type=offer.type)
            db.session.add(offer_selection)
            db.session.commit()
    
            if next_offer:
                return redirect(url_for('user.set_offer', type_id=int(type_id)+1))
        else:
            if (type_id == '2'):
                if next_offer:
                    return redirect(url_for('user.set_offer', type_id=int(type_id)+1))
            else:
                return redirect(url_for('user.set_offer', type_id=type_id))

        flash('Oferta seleccionada correctamente', 'success')
        return redirect(form.next.data or url_for('user.index'))
    return render_template('user_offer.html', form=form,
                           current_user=current_user)

@user.route('/save_user_choice', methods=['POST'])
@login_required
def save_user_choice():
    #TODO: comprobar que el usuario no haya guardado ya
    form = UserOfferForm()
    project = current_user.projects[-1] #FIXME
    for oid in form.type.data[:-1].split(','): #:-1 para quitar la última coma
        print 'saving offer id', oid
        offer_id = int(oid.strip())
        offer = Offer.query.get_or_404(offer_id) # No sería necesario si OfferSelection no guardara offer_type, que también es innecesario
        prev_offer = OfferSelection.query.filter_by(project_id=project.id, user_id=current_user.id, offer_type=offer.type).first()
        if prev_offer:
            db.session.delete(prev_offer)
            db.session.commit()
        choice = OfferSelection(offer_id=offer_id, project_id=project.id, user_id=current_user.id, offer_type=offer.type)
        db.session.add(choice)
        db.session.commit()
    return redirect(form.next.data or url_for('user.index'))




