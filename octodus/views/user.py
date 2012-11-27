# -*- coding: utf-8 -*-

import datetime

from flask import Blueprint, render_template, redirect, url_for, request, \
                flash, jsonify
                    #current_app, g
from flask.ext.login import login_required, current_user

from flaskext.mail import Message

from octodus.models import *
from octodus.decorators import admin_required
                            #keep_login_url
from octodus.forms import EditDatosForm, FollowForm, TaskForm, ProjectForm
from octodus.extensions import db, mail
from sqlalchemy import Date, cast
#import datetime


user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/')
@login_required
def index():
    return render_template('user_index.html', current_user=current_user,
                            today=datetime.datetime.now())


@user.route('/ayuda')
@login_required
def ayuda():
    return render_template('user_email.html', current_user=current_user)



@user.route('/edit_date', methods=['POST', 'GET'])
@login_required
def edit_date():
    project = current_user.projects[-1]
    form = EditDateForm(next=request.args.get('next'))
    if request.method == 'post':
        date = Session.query.filter_by(id=form.date.data).first()
        appointment = Appointment(project=project, user=current_user,
                                    session=date, date=date.begin)
        db.session.add(appointment)
        db.session.commit()
        return redirect(form.next.data or url_for('user.index'))

    dates = Session.query.\
                filter(cast(Session.begin, Date) > datetime.date.today()).all()
    form.generate_dates(dates)
    return render_template('user_edit_date.html', form=form,
                            current_user=current_user)


@user.route('/edit_datos', methods=['POST', 'GET'])
@login_required
def edit_datos():
    commit = False
    project = current_user.projects[-1]
    groups = [project, ]
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
            groups = [group, ]
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


@user.route('/projects/new', methods=['POST', 'GET'])
@user.route('/newproject', methods=['POST', 'GET'])
@login_required
def new_project():
    form = ProjectForm()
    if request.method == 'POST':
        newproject = Project(name=form.name.data, owner=current_user)
        db.session.add(newproject)
        db.session.commit()
        return redirect(url_for('user.projects'))
    return render_template('user_newproject.html', form=form,
                            current_user=current_user)


@user.route('/tasks/new', methods=['POST', 'GET'])
@user.route('/newtask', methods=['POST', 'GET'])
@login_required
def new_task():
    form = TaskForm()
    if request.method == 'POST':
        newtask = Task(name=form.name.data, owner=current_user)
        db.session.add(newtask)
        db.session.commit()
        return redirect(url_for('user.tasks'))
    return render_template('user_newtask.html', form=form,
                            current_user=current_user)


@user.route('/projects/')
@login_required
def projects(name=None):
    user = current_user
    return render_template('list.html', title="Proyectos", headers=False, 
                           objects=user.projects, fields=['name',], 
                            actions=[['Borrar', 'del', 'icon-trash']],
                            current_user=current_user)

@user.route('/projects/<name>/tasks/')
@login_required
def project_tasks(name):
    project = None
    if name:
        for each_project in current_user.projects:
            if each_project.name == name:
                project = each_project
                break
    if project:
        return render_template('list.html', title=name+"'s Tasks",
                            headers=False, 
                            objects=project.tasks, fields=['name',], 
                            actions=[['Borrar', 'del', 'icon-trash']],
                            current_user=current_user)



@user.route('/tasks')
@user.route('/<name>/tasks')
@login_required
def tasks(name=None, done=None):
    if name:
        user = User.query.filter_by(username=name).first()
    else:
        user = current_user
    tasks = user.tasks
    if done:
        done_tasks = []
        for task in tasks:
            if task.done:
                done_tasks.append(task)
        tasks = done_tasks
    return render_template('list.html', title="Tareas", headers=False, 
                           objects=tasks, fields=['name',], 
                            actions=[['Borrar', 'del', 'icon-trash']],
                            current_user=current_user)
@user.route('/done')
def done():
        return tasks(name=None, done=True)

@user.route('/private')
def private():
        return redirect('user/project/private/tasks')


@user.route('/public')
def public():
        return redirect('user/project/public/tasks')




@user.route('/inbox')
def inbox():
        return redirect('user/project/inbox/tasks')

@user.route('/timeline')
@user.route('/<project_name>/timeline')
@login_required
def timeline(project_name=None):
    if project_name:
        for each_project in current_user.projects:
            if each_project.name == project_name:
                project = each_project
                break
        users = project.users_in
    else:
        users = current_user.following
    all_tasks = []
    for followee in users:
        if followee != current_user:
            all_tasks = all_tasks + followee.tasks

    return render_template('list.html', title="Timeline", headers=False, 
                           objects=all_tasks, fields=['name',], 
                            actions=[['Borrar', 'del', 'icon-trash']],
                            current_user=current_user)



@user.route('/list')
@login_required
@admin_required
def list():
    users2 = User.query.all()
    users = users2[:]
    return render_template('list.html', title="Usuarios", objects=users,
                            fields=['name', 'surname', 'email'],
                            no_set_delete=True,
                            active='user_list',
                            actions=[['Borrar', 'del', 'icon-trash']],
                            current_user=current_user)


@user.route('/profile', methods=['GET'])
@user.route('/<name>', methods=['POST', 'GET'])
def pub(name=None):
    form = FollowForm()
    if request.method == 'POST':
        followed = User.query.filter_by(username=name).first()
        current_user.following.append(followed)
        db.session.commit()
    if current_user.is_authenticated() and \
       (current_user.username == name or name==None):
        return render_template('user_pub.html', user=current_user, form=form)
       # return redirect(url_for('user.index'))

    user = User.query.filter_by(username=name).first_or_404()
    form.follow = name
    return render_template('user_pub.html', user=user, form=form)


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
    project = current_user.projects[-1]  # FIXME
    session_id = request.args.get('session_id', None)
    form = UserAppointmentForm()
    if not session_id:
        # get all sessions for this project
        sessions = [[s.begin.date().isoformat(), int(s.id)]
                        for s in project.sessions
                            if s.begin > datetime.datetime.now()]
        sessions = sorted(sessions)
        return render_template('user_appointment.html', form=form,
                                sessions=sessions)
    else:
        # get all hours for this session
        sess = Session.query.filter_by(id=session_id).first()
        interval_timedelta = sess.end - sess.begin
        #hack so it works in python2.6
        td = interval_timedelta
        total_seconds = (td.microseconds +
                         (td.seconds + td.days * 24 * 3600)
                          * 10 ** 6) / 10 ** 6
        interval_mins = int(total_seconds / 60)
                        #int(interval_timedelta.total_seconds() / 60)
        all_hours = [sess.begin + datetime.timedelta(minutes=x)
                        for x in range(0, interval_mins, sess.block_duration)]
        all_hours_occupation = [(h, len([apn for apn in sess.appointments
                                    if apn.date == h])) for h in all_hours]
        #hours = [ (h, n) for (h, n) in all_hours_occupation
        #if n < sess.block_capacity ]
        hours = [(h, str(h).split()[1])
                    for (h, n) in all_hours_occupation
                        if n < sess.block_capacity]
        form.set_hours(hours)
        form.session.data = session_id
        return render_template('user_appointment.html',
                                form=form, hours=hours, session=sess)


@user.route('/new_appointment', methods=['POST'])
@login_required
def new_appointment_post():
    #session_id = request.args.get('session_id', None)
    form = UserAppointmentForm()
    session_id = form.session.data
    appointment_date = form.hour.data
    project = current_user.projects[-1]  # FIXME
    if not session_id or not appointment_date:
        # TODO
        flash(u'Datos actualizados incorrectamente', 'error')
        return redirect(url_for('user.new_appointment_get'))

    # Count appointments in this slot
    count = Appointment.query.\
                filter_by(session_id=session_id, date=appointment_date).count()
    sess = Session.query.filter_by(id=session_id).first()
    if count >= sess.block_capacity:
        flash(u"La hora elegida ya se ha completado", 'error')
        return redirect(url_for('user.new_appointment_get'))
        #return redirect(form.next.data or url_for('user.index'))

    previous_appointment = Appointment.query.\
                        filter_by(user=current_user, project=project).first()
    if previous_appointment:
        if previous_appointment.date < datetime.datetime.now():
            flash('Lo sentimos, su cita ya ha tenido lugar', 'error')
    #TODO #ERROR, permitimos cambiar fecha de appointment si ya ha ocurrido?
            return redirect(form.next.data or url_for('user.index'))
    #TODO elif si la fecha de modificación de appointments ya ha ocurrido,
    #no dejamos cambiar el appointment
        else:
            appointment = previous_appointment
    else:
        appointment = Appointment()
    appointment.date = appointment_date
    appointment.project = current_user.projects[-1]  # FIXME
    appointment.user = current_user
    appointment.session = Session.query.filter_by(id=session_id).first()
    db.session.commit()
    time = appointment_date.split()[1]
    (year, month, day) = appointment_date.split()[0].split('-')
    body = render_template('emails/remember_appointment.html',
                            current_user=current_user, time=time, year=year,
                            month=month, day=day)
    message = Message(subject='Recordatorio de tu cita', html=body,
                        recipients=[current_user.email])
    mail.send(message)
    flash('Cita confirmada correctamente para el ' + day + '-' + month + '-'
            + year + ' a las ' + time + ')', 'success')
    return redirect(form.next.data or url_for('user.index'))


@user.route('/set_offer/<type_id>', methods=['GET', 'POST'])
@user.route('/set_offer/', methods=['GET', 'POST'])
@login_required
def set_offer(type_id=1):
    form = UserOfferForm()
    form.set_offer_type(type_id)
    project = current_user.projects[-1]  # FIXME

    if request.method == 'POST':
        next_offer = Offer.query.filter_by(type=str(int(type_id) + 1)).first()
        if form.options.data != u'None':
            offer = Offer.query.get(int(form.options.data))
            offer_selection = OfferSelection(offer_id=offer.id,
                                project_id=project.id, user_id=current_user.id,
                                offer_type=offer.type)
            db.session.add(offer_selection)
            db.session.commit()

            if next_offer:
                return redirect(url_for('user.set_offer',
                                    type_id=int(type_id) + 1))
        else:
            if (type_id == '2'):
                if next_offer:
                    return redirect(url_for('user.set_offer',
                                    type_id=int(type_id) + 1))
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
    project = current_user.projects[-1]  # FIXME
    if len(current_user.offer_selection):
        for selection in current_user.offer_selection:
            db.session.delete(selection)
        db.session.commit()

    for oid in form.type.data[:-1].split(','): #:-1 para quitar la última coma
        print 'saving offer id', oid
        offer_id = int(oid.strip())
        offer = Offer.query.get_or_404(offer_id)
        # No sería necesario si OfferSelection no guardara offer_type,
        # que también es innecesario
        choice = OfferSelection(offer_id=offer_id, project_id=project.id,
                                user_id=current_user.id, offer_type=offer.type)
        db.session.add(choice)
        db.session.commit()
    return redirect(form.next.data or url_for('user.index'))


@user.route('/see_poll_json', methods=['GET'])
@user.route('/see_poll_json/<poll_type_param>', methods=['GET'])
@login_required
def see_poll_json(poll_type_param=None):
    project = current_user.projects[-1] 

    if poll_type_param:
        poll_types = [int(poll_type_param), ]
    else:
        poll_types = set([vote.poll_type for vote in project.poll_selection])

    total = dict()
    results = [] 
    for poll_type in poll_types:
        votes = [vote.poll_item_id for vote in project.poll_selection if
                vote.poll_type == poll_type] 

        candidates = set(votes)
        aggregated = dict()  # aggregated proffesor votes
        for candidate in candidates:
            name = PollItem.query.get(candidate).name
            count = votes.count(candidate)
            aggregated_name = dict()
           # aggregated_name['f'] = "null"
            aggregated_name['v'] = name
            aggregated_count = dict()
           # aggregated_count['f'] = "null"
            aggregated_count['v'] = count
            value = dict()
            value["c"] = [aggregated_name, aggregated_count]
            results.append(value)
    total['rows'] = results
    total['cols'] = [{'id':'','label':'Opciones','pattern':'', 
                      'type':'string'},
                     {'id':'', 'label':'Votos', 'pattern':'', 
                      'type':'number'}]
    return jsonify(total)

@user.route('/see_polls/', methods=['GET'])
@login_required
def see_polls():
    project = current_user.projects[-1]
    polls = set([vote.poll_type for vote in project.poll_selection])
    return render_template('user_see_polls.html', 
                           current_user=current_user, polls=polls)

@user.route('/set_poll_option/', methods=['GET', 'POST'])
@user.route('/set_poll_option/<type_id>', methods=['GET', 'POST'])
@login_required
def set_poll_option(type_id=1):
    form = UserPollForm()
    project = current_user.projects[-1]  # FIXME

   #     if form.options.data != u'None':
   #         poll_item = PollItem.query.get(int(form.options.data))
   #         poll_selection = PollSelection(poll_item_id=poll_item.id,
   #                                         project_id=project.id,
   #                                         user_id=current_user.id,
   #                                         poll_type=poll_item.type)
   #         db.session.add(poll_selection)
   #         db.session.commit()

    if request.method == 'POST':
        if len(current_user.poll_selection):
            for selection in current_user.poll_selection:
                db.session.delete(selection)
            db.session.commit()

        list = form.type.data[:-1].split(',') 
        for oid in list: #:-1 para quitar la última coma
            print 'saving poll item id', oid
            poll_item_id = int(oid.strip())
            poll_item = PollItem.query.get_or_404(poll_item_id)
            # No sería necesario si OfferSelection no guardara offer_type,
            # que también es innecesario
            choice = PollSelection(poll_item_id=poll_item_id, 
                                   project_id=project.id,
                                   user_id=current_user.id,
                                   poll_type=poll_item.type)
            db.session.add(choice)
            db.session.commit()
        flash('Votos emitidos correctamente', 'success')
        return redirect(form.next.data or url_for('user.index'))
   # else:
   #     return redirect(url_for('user.set_poll_option', type_id=type_id))

    form.set_poll_type(type_id)
    return render_template('user_poll.html', form=form,
                           current_user=current_user)
