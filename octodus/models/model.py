##!/usr/bin/env python
# -*- coding: utf-8 -*-


from octodus.extensions import db
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from flask import url_for

#import datetime

from werkzeug import (generate_password_hash, check_password_hash)
    #cached_property
from flask.ext.login import UserMixin

#from flask import jsonify


class Definitions(object):
    USER_TYPE_ADMIN = 1
    USER_TYPE_COORDINATOR = 2


users_props = db.Table("users_props", db.metadata,
    db.Column("user_id", db.Integer, ForeignKey("users.id")),
    db.Column("points", db.Integer),
    db.Column("task_id", db.Integer, ForeignKey("tasks.id")))

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


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    name = db.Column(db.String(64))
    surname = db.Column(db.String(128))
    email = db.Column(db.String(128))
    password_hash = db.Column(db.String(64))
    activation_key = db.Column(db.String(128))
    user_type = db.Column(db.Integer)
    points = db.Column(db.Integer)
    tasks = relationship("Task", backref="owner")
    projects = relationship("Project", backref="owner")
    following = relationship("User", secondary=users_followers, 
                             primaryjoin=users_followers.c.user_id==id,
                    secondaryjoin=users_followers.c.follower_id==id,
                             backref="followers")
#projects = relationship("Project", secondary=projects_users, backref="users")
#nodes = relationship("Node", secondary=nodes_users, backref="users")

    #def __init__(self, name, surname, email, password="", type=0):
    #    self.name = name
    #    self.surname = surname
    #    self.email = email
    #    self.password = password
    #    self.type = type

    def get_password(self):
        return ""

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

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


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    description = db.Column(db.String(256))
    duration = db.Column(db.Integer)
    done = db.Column(db.Boolean)
    added = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)
    finished = db.Column(db.DateTime)
    begin = db.Column(db.DateTime)
    deadline = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, ForeignKey("users.id"))



class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    description = db.Column(db.String(256))
    deadline = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, ForeignKey("users.id"))
    tasks = relationship("Task", secondary=projects_tasks, backref="projects")
    users = relationship("User", secondary=users_projects, backref="projects_in")

