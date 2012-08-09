##!/usr/bin/env python
# -*- coding: utf-8 -*-


from fbone.extensions import db
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *

import datetime

from werkzeug import (generate_password_hash, check_password_hash, cached_property)
from flask.ext.login import UserMixin


class Definitions(object):
    USER_TYPE_ADMIN = 1
    USER_TYPE_COORDINATOR = 2
    

nodes_professors = db.Table("nodes_professors", db.metadata,
    db.Column("node_id", db.Integer, ForeignKey("nodes.id")),
    db.Column("professor_id", db.Integer, ForeignKey("professors.id")))


projects_nodes = db.Table("projects_nodes", db.metadata,
    db.Column("project_id", db.Integer, ForeignKey("projects.id")),
    db.Column("node_id", db.Integer, ForeignKey("nodes.id")))

projects_users = db.Table("projects_users", db.metadata,
    db.Column("project_id", db.Integer, ForeignKey("projects.id")),
    db.Column("user_id", db.Integer, ForeignKey("users.id")))

projects_sessions = db.Table("projects_sessions", db.metadata,
    db.Column("project_id", db.Integer, ForeignKey("projects.id")),
    db.Column("session_id", db.Integer, ForeignKey("sessions.id")))


class Appointment(db.Model):
    __tablename__ = "appointments"
    project_id = db.Column(db.Integer, ForeignKey("projects.id"), primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"), primary_key=True)
    session_id = db.Column(db.Integer, ForeignKey("sessions.id"), primary_key=True)
    date = db.Column(db.DateTime)
    project = relationship("Project", backref="appointments")
    user = relationship("User", backref="appointments")
    session = relationship("Session", backref="appointments")
    
#    def __init__(self, date):
#        self.date = date
    
    def __str__(self):
        s = "APPOINTMENT: %s %s @ %s on %s\n" % (self.user.name, self.user.surname, self.project.name, self.date)
        return s


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    type = db.Column(db.String(128))    
    term = db.Column(db.String(32))
    users = relationship("User", secondary=projects_users, backref="projects")
    nodes = relationship("Node", secondary=projects_nodes, backref="projects")
    sessions = relationship("Session", secondary=projects_sessions, backref="projects")
    #node_id = db.Column(db.Integer, ForeignKey("nodes.id"))
    #appointments = relationship("Appointment", backref="project")
    depth = db.Column(db.Integer)
    activation_key = db.Column(db.String(128), unique=True)
    parent_id = db.Column(db.Integer, ForeignKey("projects.id"))
    #projects = relationship("Project", backref="node")
    children = relationship("Project",
                backref=backref('parent', remote_side=[id])
               )
    #sessions = relationship("Session", backref="project")
    
#    def __init__(self, name, term):
#        self.name = name
#        self.term = term

    def create(self):
        if self.depth is None:
            self.depth = 0
        if not self.activation_key:
            self.activation_key = self.nodes[0].activation_key + self.term
        if not self.name:
            self.name = self.nodes[0].name
        if not self.type:
            self.type = self.nodes[0].type
        for i in self.nodes:
            for j in i.children:
                project_already_created = db.session.query(Project).filter(Project.term==self.term).filter(Project.nodes.any(id=j.id)).all()
                if not project_already_created:
                   new_project = Project(term=self.term)
                   new_project.nodes.append(j)
                   new_project.name = j.name
                   new_project.type = j.type
                   new_project.activation_key = j.activation_key + self.term
                   new_project.depth = self.depth + 1
                   self.children.append(new_project)
                   db.session.commit()
                   new_project.create()
    
    def __str__(self):
        s = "PROJECT %s (id %d)\n" % (self.year, self.id)
        for a in self.users:
            s += "\tUSER: %s %s (id %d)\n" % (a.name, a.surname, a.id)
        return s


class Professor(db.Model):
    __tablename__ = "professors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    surname = db.Column(db.String(128))
    picture = db.Column(db.String(128))
    
#    def __init__(self, name, surname):
#        self.name = name
#        self.surname = surname
    
    def __str__(self):
        return "PROFESSOR %s %s\n" % (self.name, self.surname)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    surname = db.Column(db.String(128))
    email = db.Column(db.String(128))
    password_hash = db.Column(db.String(64))
    activation_key = db.Column(db.String(128))
    type = db.Column(db.Integer)
    #projects = relationship("Project", secondary=projects_users, backref="users")
#    nodes = relationship("Node", secondary=nodes_users, backref="users")
    
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
        return self.type == Definitions.USER_TYPE_ADMIN
    
    def is_coordinator(self):
        return self.type == Definitions.USER_TYPE_COORDINATOR

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


class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key=True)
    begin = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    block_duration = db.Column(db.Integer)
    block_capacity = db.Column(db.Integer)
    #project_id = db.Column(db.Integer, ForeignKey("projects.id"))

#    def __init__(self, begin, end, capacity_per_hour, block_duration=10):
#        self.begin = begin
#        self.end = end
#        self.capacity_per_hour = capacity_per_hour
#        self.block_duration = block_duration
    


class Node(db.Model):
    __tablename__ = "nodes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    type = db.Column(db.String(128))
    depth = db.Column(db.Integer)
    activation_key = db.Column(db.String(128), nullable=False, unique=True)
    parent_id = db.Column(db.Integer, ForeignKey("nodes.id"))
    #projects = relationship("Project", backref="node")
    children = relationship("Node",
                backref=backref('parent', remote_side=[id])
               )

#    def __init__(self, begin, end, parent_id=None):
#        self.name = name
#        self.activation_key = activation_key
#        self.parent_id = parent_id




def main():
    engine = create_engine("mysql://orlas:salro@localhost/orlas")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()


if __name__ == "__main__":
    main()
    #pass
