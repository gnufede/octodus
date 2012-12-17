##!/usr/bin/env python
# -*- coding: utf-8 -*-


from octodus.extensions import db
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from flask import url_for
import datetime
import os

#import datetime

from werkzeug import (generate_password_hash, check_password_hash)
    #cached_property
from flask.ext.login import UserMixin

#from flask import jsonify
SQLALCHEMY_DATABASE_URI = 'mysql://octodus:sudotco@localhost/octodus'

if os.environ.get('SHARED_DATABASE_URL'):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SHARED_DATABASE_URL')
if os.environ.get('DATABASE_URL'):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URI)

class Definitions(object):
    USER_TYPE_ADMIN = 1
    USER_TYPE_COORDINATOR = 2


#users_props = db.Table("users_props", db.metadata,
#    db.Column("user_id", db.Integer, ForeignKey("users.id")),
#    db.Column("points", db.Integer),
#    db.Column("task_id", db.Integer, ForeignKey("tasks.id")))

users_followers = db.Table("users_followers", db.metadata,
    db.Column("user_id", db.Integer, ForeignKey("users.id")),
    db.Column("follower_id", db.Integer, ForeignKey("users.id")))

users_projects = db.Table("users_projects", db.metadata,
    db.Column("user_id", db.Integer, ForeignKey("users.id")),
    db.Column("user_role", db.Integer),
    db.Column("project_id", db.Integer, ForeignKey("projects.id")))

projects_tasks = db.Table("projects_tasks", db.metadata,
    db.Column("project_id", db.Integer, ForeignKey("projects.id")),
    db.Column("task_id", db.Integer, ForeignKey("tasks.id")))


class Prop(db.Model):
    __tablename__ = "users_props"
    user_id = db.Column(db.Integer, ForeignKey("users.id"), primary_key=True)
    task_id = db.Column(db.Integer, ForeignKey("tasks.id"), primary_key=True)
    points = db.Column(db.Integer, default=1)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, ForeignKey("comments.id"))
    children = relationship ("Comment", backref=backref('parent',
                                                        remote_side=[id]))
    task_id = db.Column(db.Integer, ForeignKey("tasks.id"))
    task = relationship("Task", backref="comments")
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User", backref="comments")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.datetime.utcnow,
                         onupdate=datetime.datetime.utcnow)
    content = db.Column(db.Text)
#    upvotes = db.Column(db.Integer)
#    downvotes = db.Column(db.Integer)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    surname = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    password_hash = db.Column(db.String(64))
    activation_key = db.Column(db.String(128))
    user_type = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_action = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    points = db.Column(db.Integer, default=0)
    tasks = relationship("Task", backref="owner", primaryjoin="and_(User.id==Task.owner_id)")
    sent_tasks = relationship("Task", backref="sender", primaryjoin="and_(User.id==Task.sender_id)")
    #tasks = relationship("Task", backref="owner")
    projects = relationship("Project", backref="owner")
    following = relationship("User", secondary=users_followers, 
                             primaryjoin=users_followers.c.user_id==id,
                    secondaryjoin=users_followers.c.follower_id==id,
                             backref="followers")
    props = relationship("Prop", backref="propped_users")
#projects = relationship("Project", secondary=projects_users, backref="users")
#nodes = relationship("Node", secondary=nodes_users, backref="users")

    #def __init__(self, name, surname, email, password="", type=0):
    #    self.name = name
    #    self.surname = surname
    #    self.email = email
    #    self.password = password
    #    self.type = type

    def get_undone_tasks(self):
        return len([task for task in self.tasks if not task.done])

    def get_password(self):
        return ""

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def timeline(self, project_name=None, user=None):
        project = None
        userid = None
        users = None
        self_timeline = None
        if project_name:
            for each_project in self.projects:
                if each_project.name == project_name:
                    project = each_project
                    break
            if project:
                users = project.users
        elif user:
            self_timeline = True
            users = [user,]
        else:
            users = self.following
        all_tasks = []
        if users:
            for followee in users:
                if followee != self or self_timeline:
                    for project in followee.projects:
                        if project.name == "Public" or (self in project.users):
                            for task in project.tasks:
                                if task.owner == followee and task not in all_tasks:
                                    all_tasks.append(task)
        return sorted(all_tasks, key=lambda task: task.modified, reverse=True)

    def getProjs(self, user):
        all_projects = self.projects
        return_projects = []
        for project in all_projects:
            if user in project.users:
                return_projects.append(project)
        return return_projects


    def follow(self, user):
        if user not in self.following:
            self.following.append(user)


    def unfollow(self, user):
        if user in self.following:
            self.following.remove(user)


    password = property(get_password, set_password)

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.user_type == Definitions.USER_TYPE_ADMIN

    def is_coordinator(self):
        return self.user_type == Definitions.USER_TYPE_COORDINATOR

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter(User.email == email).first()
        if not user:
            user = cls.query.filter(User.username == email).first()
        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False
        return user, authenticated

    @classmethod
    def search(cls, keywords):
        criteria = []
        for keyword in keywords.split():
            keyword = '%' + keyword + '%'
            criteria.append(User.email.ilike(keyword))
        q = reduce(db.and_, criteria)
        return cls.query.filter(q)

    def getContactNames(self):
        return [contact.username for contact in self.following 
                    if self in contact.following]

    def getContacts(self, projectname=None):
        if not projectname:
            return [contact for contact in self.following 
                    if self in contact.following]
        contacts = [contact for contact in self.following 
                    if self in contact.following]
        project = Project.query.filter_by(name=projectname, owner=self).first()
        if project:
            return [contact for contact in contacts
                           if contact in project.users]
        else: return []

    def prop(self, task, points=1):
        if task.owner != self and self.points >= points:
            if self.id not in [prop.user_id for prop in task.props]:
                prop = Prop(user_id=self.id, task_id=task.id, points=points)
                db.session.add(prop)
            else:
                prop = Prop.query.filter_by(user_id=self.id, task_id=task.id).first()
                prop.points += points
            self.points -= points
            db.session.commit()
            return True
        return False

    def unprop(self, task, points=1):
        if task.owner != self:
            if self.id in [prop.user_id for prop in task.props]:
                prop = Prop.query.filter_by(user_id=self.id, task_id=task.id).first()
                if prop.points > 0:
                    prop.points -= points
                    self.points += points
                if prop.points == 0:
                    db.session.delete(prop)
                db.session.commit()
                return True
        return False





class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    description = db.Column(db.Text)
    priority = db.Column(db.Integer, default=0)
    urgency = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Integer, default=30)
    earned_points = db.Column(db.Integer, default=0)
    done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.datetime.utcnow,
                         onupdate=datetime.datetime.utcnow)
    finished = db.Column(db.DateTime)
    begin = db.Column(db.DateTime)
    deadline = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, ForeignKey("users.id"))
    sender_id = db.Column(db.Integer, ForeignKey("users.id"))
    #sender = relationship("User", backref="sent_tasks")
    props = relationship("Prop", backref="propped_tasks")

    
    def get_props(self):
        return sum([prop.points for prop in self.props])

    def get_propped_users(self):
        tostring = '';
        for prop in self.props:
            tostring += str(prop.propped_users.username)+\
                        '('+str(prop.points)+'), '
        return tostring[:-2]

    def get_propped_usernames(self):
        return [prop.propped_users.username for prop in self.props] 


    def getProjs(self, user):
        all_projects = self.projects
        return_projects = []
        for project in all_projects:
            if user in project.users or project.name=='Public':
                return_projects.append(project)
        return return_projects


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    description = db.Column(db.String(256))
    deadline = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, ForeignKey("users.id"))
    tasks = relationship("Task", secondary=projects_tasks, backref="projects")
    users = relationship("User", secondary=users_projects, backref="projects_in")

    def get_undone_tasks(self):
        return len([task for task in self.tasks if not task.done])

    def addTask(self, task):
        self.tasks.append(task)
        db.session.commit()

