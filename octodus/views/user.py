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
from octodus.forms import EditDatosForm, FollowForm, TaskForm, ProjectForm, CommentForm
from octodus.extensions import db, mail
from sqlalchemy import Date, cast
import re
import math
from random import randint
import json
import hashlib
#import datetime


user = Blueprint('user', __name__, url_prefix='/user')


timeline_fields=['id','owner', 'props', 'earned_points','created_at', 'name', 'projects']
               


@user.route('/')
@login_required
def index():
    #return tasks(name=None, done=False)
    return redirect(url_for('user.tasks'))
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
@user.route('/project/<name>', methods=['POST', 'GET'])
@login_required
def new_project(name=None):
    if name and (name not in [project.name for project in current_user.projects]):
        newproject = Project(name=name, owner=current_user)
        db.session.add(newproject)
        db.session.commit()
        return jsonify({'1':True})
    form = ProjectForm()
    if name:
        form.name.data = name
    if request.method == 'POST' or name:
        name = form.name.data
        if name not in [project.name for project in current_user.projects]:
            newproject = Project(name=name, owner=current_user)
            db.session.add(newproject)
            db.session.commit()
            return redirect(url_for('user.projects'))
    return render_template('user_newproject.html', form=form,
                            current_user=current_user)


@user.route('/projects/')
@login_required
def projects(name=None):
    user = current_user
    return render_template('list.html', title="Proyectos", headers=False, 
                           objects=user.projects, fields=['name',], 
                            actions=[['Borrar', 'del', 'icon-trash']],
                            current_user=current_user)


@user.route('/projects/del/<id>')
@login_required
def project_delete(id):
    project = Project.query.filter_by(name=id, owner=current_user).first()
    if not project:
        project = Project.query.get(id)
    if project.owner == current_user and\
       project.name not in ['Inbox', 'Private', 'Public']:
        db.session.delete(project)
        db.session.commit()
        return jsonify({'1':True})
    return redirect(url_for('user.projects'))


@user.route('/project/<name>/set/<task_id>', methods=['POST', 'GET'])
@login_required
def set_project_tasks(name, task_id):
    task = Task.query.get(task_id)
    if not task or (task and task.owner != current_user and task.sender != current_user):
        return jsonify({'1':False})
    project = Project.query.get(name)
    if not project:
        proj_name = re.compile('^'+name+'$', re.I)
        for each_project in current_user.projects:
            if proj_name.match(each_project.name):
                project = each_project
    if project and project.owner == current_user:
        if task not in project.tasks:
            project.addTask(task)
            if project.name != 'Inbox':
                inbox = [proj for proj in current_user.projects 
                         if proj.name == 'Inbox']
                if task in inbox[0].tasks:
                    inbox[0].tasks.remove(task)
                    db.session.commit()
            return jsonify({'1':True})
    return redirect('user/tasks/'+name)


@user.route('/project/<name>/unset/<task_id>', methods=['POST', 'GET'])
@login_required
def unset_project_tasks(name, task_id):
    task = Task.query.get(task_id)
    if not task or (task and task.owner != current_user and task.sender != current_user):
        return jsonify({'1':False})
    project = Project.query.get(name)
    if not project:
        proj_name = re.compile('^'+name+'$', re.I)
        for each_project in current_user.projects:
            if proj_name.match(each_project.name):
                project = each_project
    if project and project.owner == current_user:
        if task in project.tasks:
            project.tasks.remove(task)
            db.session.commit()
            if task.owner != current_user:
                return jsonify({'1':True})
        in_project = None
        for project in current_user.projects:
            if task in project.tasks:
                in_project = True
        if not in_project: 
            inbox = [proj for proj in current_user.projects 
                     if proj.name == 'Inbox']
            inbox[0].tasks.append(task)
            db.session.commit()
        return jsonify({'1':True})
    #for project in current_user.projects:
    #    if project.name == name:
    #        for task in current_user.tasks:
    #            if task.id == task_id:
    #                project.addTasks(task)
    #                db.session.commit()
    return jsonify({'1':False})
    return redirect('user/tasks/'+name)


@user.route('/projects/<name>')
@user.route('/tasks/<name>')
@login_required
def project_tasks(name):
    project = None
    newtaskform = TaskForm()
    users = current_user.getContacts()
    proj_name = re.compile('^'+name+'$', re.I)
    timeline=current_user.timeline(name)
    timeline_actions=[]
    if proj_name.match('done'):
        return redirect(url_for('user.done'))
    else:
        for each_project in current_user.projects:
            if proj_name.match(each_project.name):
                project = each_project
                users = current_user.getContacts(project.name)
                users = sorted(users, key=lambda user: user.points, reverse=True)

                contacts = dict()
                for contact in current_user.following:
                    if current_user in contact.following:
                        contacts[str(contact.id)] = contact.username
                tasks = project.tasks
                tasks = sorted(tasks, key=lambda task: task.modified, reverse=True)
                tasks = sorted(tasks, key=lambda task: task.get_props(), reverse=True)
                tasks = sorted(tasks, key=lambda task: int(task.done))
                #tasks = sorted(tasks, key=lambda task: task.earned_points, reverse=True)
                return render_template('tasklist.html', title=name+"'s tasks", headers=False, 
                           tasks=tasks, 
                            fields=['id','name', 'props', 'earned_points', 'created_at','sender', 'owner', 'projects', 'description'], 
                            actions=[['Edit', 'edit', 'icon-pencil'],['Start', 'start', 'icon-play'],['Mark done', 'do', 'icon-ok'],['Send', '', 'icon-share-alt'], ['Delete', 'del', 'icon-trash']],
                           contacts=json.dumps(contacts),
                            timeline=timeline,
                            timeline_fields=timeline_fields,
                            timeline_actions=timeline_actions,
                            objects=users,
                            usersactions=[['Follow', 'follow', 'follow icon-plus'],['Unfollow', 'unfollow', 'unfollow icon-remove']],
                            usersfields=['id','username','points', 'projects'],
                            cls='tasklist',
                            project = project,
                            commentform = CommentForm(),
                            newtaskform=newtaskform,
                            current_user=current_user, active=each_project.name)
    return redirect(url_for('user.tasks'))


@user.route('/followers/')
@user.route('/<name>/followers/')
@login_required
def followers(name=None):
    if name:
        return redirect('user/contacts/'+name+'/followers')
    return redirect('user/contacts/followers')


@user.route('/following/')
@user.route('/<name>/following/')
@login_required
def following(name=None):
    if name:
        return redirect('user/contacts/'+name+'/following')
    return redirect('user/contacts/following')

@user.route('/users/')
@user.route('/users/search/<query>')
@login_required
def users(query=None):
    newtaskform = TaskForm()
    active=None
    timeline=current_user.timeline()
    timeline_actions=[]
    if not query:
        users = User.query.all()
    else:
        users = User.query.all()
 #       users = User.search(query).paginate(1,1)
    contacts = sorted(users, key=lambda contact: contact.points, reverse=True)
    return render_template('userlist.html', title="All users", headers=False, 
                           objects=contacts, 
                            fields=['id','username','points', 'projects'], 
                            actions=[['Follow', 'follow', 'follow icon-plus'],['Unfollow', 'unfollow', 'unfollow icon-trash']],
                           active=active,
                           cls='userlist',
                            timeline=timeline,
                            timeline_fields=timeline_fields,
                            timeline_actions=timeline_actions,
                           contacts=[],
                            commentform = CommentForm(),
                           newtaskform=newtaskform,
                           project=None,
                            current_user=current_user)

@user.route('/contacts/')
@user.route('/contacts/<name>')
@user.route('/contacts/<name>/<followho>')
@login_required
def contacts(name=None, followho=None):
    active = None
    project = None
    newtaskform = TaskForm()
    title = ""
    if name != "following" and name != "followers":
        if followho:
            user = User.query.filter_by(username=name).first()
            if followho == "following":
                contacts = user.following
                title = user.username + " follows"
            elif followho == "followers":
                contacts = user.followers
                title = user.username + "'s followers"
            else:
                contacts = user.getContacts()
                title = user.username + "'s contacts (following each other)"
            name = None
        else:
            contacts = current_user.getContacts()
            title = "My contacts (following each other)"
    elif name == "following":
        contacts = current_user.following
        name = None
        title = "I follow"
    elif name == "followers":
        contacts = current_user.followers
        title = "My followers"
        name = None
    timeline=current_user.timeline(name)
    timeline_actions=[]
    if name:
        proj_name = re.compile('^'+name+'$', re.I)
        for each_project in current_user.projects:
            if proj_name.match(each_project.name):
                project = each_project
        contacts = current_user.getContacts(name)
        title = project.name+"'s contacts (following each other)"
        
    contacts = sorted(contacts, key=lambda contact: contact.points, reverse=True)
    return render_template('userlist.html', title=title, headers=False, 
                           objects=contacts, 
                            fields=['id','username','points', 'projects'], 
                            actions=[['Follow', 'follow', 'follow icon-plus'],['Unfollow', 'unfollow', 'unfollow icon-trash']],
                           active=active,
                           cls='userlist',
                            timeline=timeline,
                            timeline_fields=timeline_fields,
                            timeline_actions=timeline_actions,
                           contacts=[],
                            commentform = CommentForm(),
                           newtaskform=newtaskform,
                           project=project,
                            current_user=current_user)


#@user.route('/')
@user.route('/tasks/')
@login_required
def tasks(name=None, done=None):
    active = None
    users = current_user.getContacts()
    users = sorted(users, key=lambda user: user.points, reverse=True)
    timeline_actions=[]
    newtaskform = TaskForm()
    if name:
        user = User.query.filter_by(username=name).first()
    else:
        user = current_user
    tasks = user.tasks
    if done and done=="done":
        done_tasks = [task for task in tasks
                            if task.done]
        tasks = done_tasks
        active = "Done"
    if done and done=="sent_received":
        active = "sent_received"
        from sqlalchemy import and_
        received_tasks =  Task.query.filter(
            and_ (Task.owner == current_user,Task.sender != current_user)).all()
        sent_tasks =  Task.query.filter(
            and_(Task.sender==current_user, Task.owner != current_user)
        ).all()
        sent_received_tasks = received_tasks + sent_tasks
        tasks = sent_received_tasks
    if done and done=="done_sent":
        from sqlalchemy import and_
        sent_tasks =  Task.query.filter(
            and_(Task.sender==current_user, Task.owner != current_user)
        ).all()
        done_tasks = [task for task in tasks
                            if task.done]
        sent_received_tasks = done_tasks + sent_tasks
        tasks = sent_received_tasks

    contacts = dict()
    for contact in user.following:
        if current_user in contact.following:
            contacts[str(contact.id)] = contact.username

    tasks = sorted(tasks, key=lambda task: task.modified, reverse=True)
    tasks = sorted(tasks, key=lambda task: task.get_props(), reverse=True)
    tasks = sorted(tasks, key=lambda task: int(task.done))
    #tasks = sorted(tasks, key=lambda task: task.earned_points, reverse=True)
    timeline=current_user.timeline()
    return render_template('tasklist.html', title="Tareas", headers=False, 
                           tasks=tasks, 
                            #fields=['id','name', 'props', 'earned_points',  'created_at','sender', 'projects'], 
                            fields=['id','name', 'props', 'earned_points', 'created_at','sender', 'owner', 'projects', 'description'], 
                            actions=[['Edit', 'edit', 'icon-pencil'],['Start', 'start', 'icon-play'],['Mark done', 'do', 'icon-ok'],['Send', '', 'icon-share-alt'], ['Delete', 'del', 'icon-trash']],
                           active=active,
                           cls='tasklist',
                            timeline=timeline,
                            timeline_fields=timeline_fields,
                            timeline_actions=timeline_actions,
                            objects=users,
                            usersactions=[['Follow', 'follow', 'follow icon-plus'],['Unfollow', 'unfollow', 'unfollow icon-trash']],
                            usersfields=['id','username','points', 'projects'],
                           contacts=json.dumps(contacts),
                           project=None,
                            commentform = CommentForm(),
                           newtaskform=newtaskform,
                            current_user=current_user)

@user.route('/tasks/done_sent')
def done_sent():
        return tasks(name=None, done="done_sent")

@user.route('/tasks/sent_received')
def sent_received():
        return tasks(name=None, done="sent_received")

@user.route('/tasks/done')
def done():
        return tasks(name=None, done="done")

@user.route('/Private/')
def private():
        return redirect('user/tasks/Private')


@user.route('/Public/')
def public():
        return redirect('user/tasks/Public')


@user.route('/Inbox/')
def inbox():
        return redirect('user/tasks/Inbox')


@user.route('/tasks/send/<taskid>/<userid>', methods=['POST', 'GET'])
@login_required
def send_task(taskid=None, userid=None):
    if taskid:
        task = Task.query.filter_by(name=userid, owner=current_user).first()
    if not task:
        task = Task.query.get(taskid)
    if userid:
        followed = User.query.filter_by(username=userid).first()
    if not followed:
        followed = User.query.get(userid)
    if task and (task.owner == current_user) and\
       followed and followed!=current_user and\
       (followed in current_user.getContacts()):
        if current_user.points > 5 :
            task.owner = followed
            current_user.points = current_user.points - 5
            owner = followed
            inbox = [project for project in owner.projects
                 if project.name=='Inbox']
            if inbox:
                task.projects.append(inbox[0])
            db.session.commit()
            return jsonify({'1':True})
    return jsonify({'1':False})


@user.route('/comment/<id>.json', methods=['POST', 'GET'])
def comment_json(id):
    comment=Comment.query.get(id)
    dict_comment = dict((col, getattr(comment, col)) for col in comment.__table__.columns.keys())
    for (key,value) in dict_comment.iteritems():
        if isinstance(value, datetime.datetime):
            dictcomment[key] = value.date().isoformat()
    return jsonify(dict_comment)



@user.route('/comments/<id>.json', methods=['POST', 'GET'])
def comments_json(id):
    task=Task.query.get(id)
    if task:
        comments = task.comments
        if comments:
            dict_comments = dict()
            for comment in comments:
                dict_comment = dict((col, getattr(comment, col)) for col in comment.__table__.columns.keys())
                for (key,value) in dict_comment.iteritems():
                    if isinstance(value, datetime.datetime):
                        dict_comment[key] = value.isoformat()
                dict_comment['username'] = User.query.get(dict_comment['user_id']).username
                m = hashlib.md5()
                m.update(User.query.get(dict_comment['user_id']).email)
                dict_comment['avatar'] = 'http://www.gravatar.com/avatar/'+m.hexdigest()+'?s=40&amp;d=mm&amp;r=g'
                dict_comments[str(comment.id)] = dict_comment
            return jsonify(dict_comments)
    return jsonify(dict())


@user.route('/comments/del/<id>', methods=['POST', 'GET'])
def edit_comment(id):
    form = CommentForm()
    comment = Comment.query.get(id)
    if request.method == 'POST' and (comment.owner==current_user or\
       comment.task.owner == current_user):
        for child in comment.children:
            child.parent = comment.parent
        db.session.remove(comment)
        db.session.commit()
        return jsonify({'1':True})
    return jsonify({'1':False})




@user.route('/comments/edit/<id>', methods=['POST', 'GET'])
def edit_comment(id):
    form = CommentForm()
    comment = Comment.query.get(id)
    if request.method == 'POST' and comment.owner==current_user:
        form.populate_obj(comment)
        db.session.commit()
        return jsonify({'1':True})
    return jsonify({'1':False})


@user.route('/comments/reply/<id>', methods=['POST', 'GET'])
def reply_comment(id):
    form = CommentForm()
    if request.method == 'POST':
        comment = Comment()
        form.populate_obj(comment)
        parent = Comment.query.get(id)
        comment.parent_id = id
        comment.task_id = parent.task_id
        comment.user_id = current_user.id
        db.session.add(comment)
        db.session.commit()
        return jsonify({'1':True})
    return jsonify({'1':False})


@user.route('/tasks/comment/<id>', methods=['POST', 'GET'])
def comment_task(id):
    form = CommentForm()
    if request.method == 'POST':
        comment = Comment()
        form.populate_obj(comment)
        comment.task_id=id
        comment.user_id=current_user.id
        db.session.add(comment)
        db.session.commit()
        return jsonify({'1':True})
    return jsonify({'1':False})


@user.route('/tasks/edit/<id>', methods=['POST', 'GET'])
def edit_task(id):
    form = TaskForm()
    if request.method == 'POST':
        task = Task.query.get(id)
        if task.owner == current_user:
            form.populate_obj(task)
            db.session.commit()
            return jsonify({'1':True})
    return jsonify({'1':False})

@user.route('/task/<id>.json', methods=['GET'])
def task_json(id):
    task=Task.query.get(id)
    if task.owner == current_user:
        dictask = dict((col, getattr(task, col)) for col in task.__table__.columns.keys())
        for (key,value) in dictask.iteritems():
            if isinstance(value, datetime.datetime):
                dictask[key] = value.date().isoformat()
        return jsonify(dictask)


@user.route('/tasks/new/<name>', methods=['POST', 'GET'])
@user.route('/tasks/new/', methods=['POST', 'GET'])
@user.route('/newtask/', methods=['POST', 'GET'])
@login_required
def new_task(name=None):
    form = TaskForm()
    owner = current_user
    project = None

    if request.method == 'POST':
        name = form.name.data
        if name[0] == '@' and current_user.points > 5:
            username, space, name = name[1:].partition(' ')
            allusers = User.query.all()
            username = re.compile('^'+username+'$', re.I)
            for each_user in allusers:
                if username.match(each_user.username):
                    owner = each_user
        elif name[0] == '+': 
            project_name, space, name = name[1:].partition(' ')
            proj_name = re.compile('^'+project_name+'$', re.I)
            for each_project in current_user.projects:
                if proj_name.match(each_project.name):
                    project = each_project

        if owner != current_user:
            if owner not in current_user.getContacts():
                return redirect(url_for('user.tasks'))
        newtask = Task(name=name, owner=owner, sender=current_user)
        if form.description.data:
            newtask.description = form.description.data
        if form.priority.data:
            newtask.priority = form.priority.data
        if form.duration_minutes.data:
            newtask.duration_minutes = form.duration_minutes.data
        if form.deadline.data:
            newtask.deadline = form.deadline.data
        if project:
            newtask.projects.append(project)
        else:
            inbox = [project for project in current_user.projects
                        if project.name=='Inbox']
            if inbox:
                newtask.projects.append(inbox[0])
            if owner != current_user:
                inbox = [project for project in owner.projects
                     if project.name=='Inbox']
                if inbox and inbox not in newtask.projects:
                    newtask.projects.append(inbox[0])
        db.session.add(newtask)
        db.session.commit()
        if owner != current_user:
            current_user.prop(newtask)
            flash('You have sent '+newtask.name+' to '+owner.username+' and propped for '+str(1)+' points!', 'success')
        return jsonify({'1':True})
    return render_template('user_newtask.html', form=form,
                            current_user=current_user)


@user.route('/tasks/start/<id>')
@login_required
def task_start(id):
    task = Task.query.get(id)
    if task.owner == current_user:
        if not task.done:
            task.begin = datetime.datetime.now()
            task.modified = task.begin
            db.session.commit()
            return jsonify({'1':True})
    return jsonify({'1':False})


@user.route('/tasks/do/<id>')
@login_required
def task_do(id):
    task = Task.query.get(id)
    if task.owner == current_user:
        if not task.done:
            task.finished = datetime.datetime.now()
            task.modified = task.finished
            started = [task.created_at, current_user.last_action]\
                        [task.created_at < current_user.last_action]
            started = [started, task.begin][bool(task.begin)]
            difference = task.finished - started
            my_difference = 90
            if difference.days < 1 and difference.seconds < (60*90):
                my_difference = difference.seconds/60
            task.duration_minutes = my_difference
            points = task.earned_points
            if points == 0:
                if task.duration_minutes >= 32:
                    points = int(math.sin(task.duration_minutes/20.0)+1.001 * 5)
                else:
                    points = int(math.sin(task.duration_minutes/20.0) * 10)

                multip = [1,((len(task.props)**1.2) * 2.1)][bool(len(task.props))]
                points = math.ceil((points + randint(0, 4)) * multip)
                points = [1,points][bool(points)]

            task.earned_points = points
            current_user.points = current_user.points + points
            current_user.last_action = task.finished
        else:
            task.finished = None 
            current_user.points = current_user.points-task.earned_points
        task.done = not task.done
        db.session.commit()
        return jsonify({'1':True})
    return redirect(url_for('user.tasks'))


@user.route('/done/del/<id>')
@user.route('/tasks/del/<id>')
@login_required
def task_delete(id):
    task = Task.query.get(id)
    if task.owner == current_user:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'1':True})
    return redirect(url_for('user.tasks'))

@user.route('/prop/<id>/')
@user.route('/prop/<id>/<value>/')
@user.route('/contacts/prop/<id>/')
@user.route('/contacts/prop/<id>/<value>/')
@user.route('/timeline/prop/<id>/')
@user.route('/timeline/prop/<id>/<value>/')
@user.route('/tasks/prop/<id>/')
@user.route('/tasks/prop/<id>/<value>/')
@login_required
def task_prop(id, value=1):
    task = Task.query.get(id)
    if current_user.prop(task, value):
        flash('You have propped '+task.name+' for '+str(value)+' points!', 'success')
        return jsonify({'1':True})
    return redirect(url_for('user.timeline'))



@user.route('/unprop/<id>/<value>/')
@user.route('/contacts/unprop/<id>/')
@user.route('/contacts/unprop/<id>/<value>/')
@user.route('/timeline/unprop/<id>/')
@user.route('/timeline/unprop/<id>/<value>/')
@user.route('/tasks/unprop/<id>/')
@user.route('/tasks/unprop/<id>/<value>/')
@login_required
def task_unprop(id, value=1):
    task = Task.query.get(id)
    if current_user.unprop(task, value):
        flash('You have unpropped '+task.name+' for '+str(value)+' points :(', 'success')
        return jsonify({'1':True})
    return redirect(url_for('user.timeline'))



@user.route('/timeline/')
@user.route('/timeline/<project_name>')
@login_required
def timeline(project_name=None):
    if project_name:
        for each_project in current_user.projects:
            if each_project.name == project_name:
                project = each_project
                break
        users = project.users
    else:
        users = current_user.following
    all_tasks = []
    for followee in users:
        if followee != current_user:
            for project in followee.projects:
                if project.name == "Public" or (current_user in project.users):
                    for task in project.tasks:
                        if task not in all_tasks:
                            all_tasks.append(task)
    all_tasks = sorted(all_tasks, key=lambda task: task.modified).reverse()
            #for task in followee.tasks:
            #    task.props_n = len(task.props)
            #    all_tasks.append(task)

    fields=['id','owner', 'created_at', 'props', 'name', 'projects']
    actions=[['Prop', 'prop', 'icon-thumbs-up']]
    return all_tasks
    return render_template('timeline.html', title="Timeline", headers=False, 
                           objects=all_tasks,
                           cls="timeline",
                            fields=['id','owner', 'created_at', 'props', 'name', 'projects'], 
                            actions=[['Prop', 'prop', 'icon-thumbs-up']],
                           contacts=[],
                            current_user=current_user)



@user.route('/list')
@login_required
def list():
    users2 = User.query.order_by(User.points.desc()).all()
    users = users2[:]

    return render_template('list.html', title="Usuarios", objects=users,
                            fields=['username','points'],
                            no_set_delete=True,
                            active='user_list',
                            actions=[['Follow', 'follow', 'icon-plus']],
                            current_user=current_user)


@user.route('/profile', methods=['GET'])
@user.route('/users/<name>', methods=['POST', 'GET'])
@user.route('/<name>', methods=['POST', 'GET'])
def pub(name=None):
    form = FollowForm()
    timeline_actions=[]
    user = None
    if request.method == 'POST':
        followed = User.query.filter_by(username=name).first()
        if followed in current_user.following:
            current_user.following.remove(followed)
        else:
            current_user.following.append(followed)
        db.session.commit()
#    if current_user.is_authenticated() and \
#       (current_user.username == name or name==None):
#        return render_template('user_pub.html', user=current_user, form=form)
       # return redirect(url_for('user.index'))
    if not name:
        user = current_user
    else:
        proj_name = re.compile('^'+name+'$', re.I)
        for each_project in current_user.projects:
            if proj_name.match(each_project.name):
                project = each_project
                return redirect('user/contacts/'+name)

    if not user:
        user = User.query.filter_by(username=name).first_or_404()
    timeline=current_user.timeline(user=user)
    form.follow = name

    if user not in current_user.following:
        form.submit.label.text = "Follow"
    else:
        form.submit.label.text = "Unfollow"

    contacts = user.getContacts()
        
    contacts = sorted(contacts, key=lambda contact: contact.points, reverse=True)
    return render_template('user_pub.html', user=user, form=form,
                            timeline=timeline,
                            timeline_fields=timeline_fields,
                            timeline_actions=timeline_actions,
                            commentform = CommentForm(),
                            newtaskform = TaskForm(),
                            objects=contacts, 
                            fields=['id','username','points', 'projects'], 
                            actions=[['Follow', 'follow', 'follow icon-plus'],['Unfollow', 'unfollow', 'unfollow icon-trash']],
                          
                          )


@user.route('/users/follow/<name>', methods=['POST', 'GET'])
@user.route('/contacts/follow/<name>', methods=['POST', 'GET'])
@user.route('/follow/<name>', methods=['POST', 'GET'])
@login_required
def follow(name=None):
    if name:
        followed = User.query.filter_by(username=name).first()
    if not followed:
        followed = User.query.get(name)
    if followed and\
         current_user != followed and followed not in current_user.following:
            current_user.following.append(followed)
            db.session.commit()
       # return redirect(url_for('user.index'))
            return jsonify({'1':True})


@user.route('/users/unfollow/<name>', methods=['POST', 'GET'])
@user.route('/contacts/unfollow/<name>', methods=['POST', 'GET'])
@user.route('/unfollow/<name>', methods=['POST', 'GET'])
@login_required
def unfollow(name=None):
    if name:
        followed = User.query.filter_by(username=name).first()
    if not followed:
        followed = User.query.get(name)
    if followed and\
          followed in current_user.following:
            current_user.following.remove(followed)
            db.session.commit()
       # return redirect(url_for('user.index'))
            return jsonify({'1':True})


@user.route('/project/<name>/adduser/<username>', methods=['POST', 'GET'])
@login_required
def project_adduser(name=None, username=None):
    try:
        project = Project.query.get(name) 
    except:
        project = Project.query.filter_by(name=name, owner=current_user).first()

    try:
        followed = User.query.get(username)
    except:
        followed = User.query.filter_by(username=username).first()
    
    if project and followed and (followed not in project.users) and (project.owner == current_user):
        project.users.append(followed)
        db.session.commit()
       # return redirect(url_for('user.index'))
        return jsonify({'1':True})
    return jsonify({'1':False})

@user.route('/project/<name>/deluser/<username>', methods=['POST', 'GET'])
@login_required
def project_deluser(name=None, username=None):
    project = Project.query.get(name)
    followed = User.query.get(username)
    if not project:
        project = Project.query.filter_by(name=name, owner=current_user).first()
    if not followed:
        followed = User.query.filter_by(username=username).first()
    if followed in project.users and project.owner == current_user:
        project.users.remove(followed)
        db.session.commit()
       # return redirect(url_for('user.index'))
        return jsonify({'1':True})






@user.route('/del/<id>')
@login_required
@admin_required
def delete(id):
    user = User.query.filter_by(id=id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user.list'))

