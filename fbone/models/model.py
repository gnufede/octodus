#!/usr/bin/env python
# -*- coding: utf-8 -*-


from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *

import datetime

from werkzeug import (generate_password_hash, check_password_hash, cached_property)
from flask.ext.login import UserMixin


Base = declarative_base()


nodes_professors = Table("nodes_professors", Base.metadata,
    Column("node_id", Integer, ForeignKey("nodes.id")),
    Column("professor_id", Integer, ForeignKey("professors.id")))


projects_users = Table("projects_users", Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id")),
    Column("user_id", Integer, ForeignKey("users.id")))


class Appointment(Base):
    __tablename__ = "appointments"
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), primary_key=True)
    date = Column(DateTime)
    project = relationship("Project", backref="appointments")
    user = relationship("User", backref="appointments")
    session = relationship("Session", backref="appointments")
    
    def __init__(self, date):
        self.date = date
    
    def __str__(self):
        s = "APPOINTMENT: %s %s @ %s on %s\n" % (self.user.name, self.user.surname, self.project.name, self.date)
        return s


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    term = Column(String(30))
    users = relationship("User", secondary=projects_users, backref="projects")
    node_id = Column(Integer, ForeignKey("nodes.id"))
    #appointments = relationship("Appointment", backref="project")
    sessions = relationship("Session", backref="project")
    
    def __init__(self, name, term):
        self.name = name
        self.term = term
    
    def __str__(self):
        s = "PROJECT %s (id %d)\n" % (self.year, self.id)
        for a in self.users:
            s += "\tUSER: %s %s (id %d)\n" % (a.name, a.surname, a.id)
        return s


class Professor(Base):
    __tablename__ = "professors"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    surname = Column(String(100))
    picture = Column(String(100))
    
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname
    
    def __str__(self):
        return "PROFESSOR %s %s\n" % (self.name, self.surname)


class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    surname = Column(String(128))
    email = Column(String(128))
    password_hash = Column(String(50))
    activation_key = Column(String(128))
    type = Column(Integer)
    
    def __init__(self, name, surname, email, password="", type=0):
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password
        self.type = type

    def get_password(self):
        return ""

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    password = property(get_password, set_password)

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password_hash, password)

    @classmethod
    def authenticate(cls, login, password):
        user = cls.query.filter(User.email == login).first()
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


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    begin = Column(DateTime)
    end = Column(DateTime)
    block_duration = Column(Integer)
    block_capacity = Column(Integer)
    project_id = Column(Integer, ForeignKey("projects.id"))

    def __init__(self, begin, end, capacity_per_hour, block_duration=10):
        self.begin = begin
        self.end = end
        self.capacity_per_hour = capacity_per_hour
        self.block_duration = block_duration
    


class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    activation_key = Column(String(128), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey("nodes.id"))
    parent = relationship("Node")
    projects = relationship("Project", backref="node")

    def __init__(self, begin, end, parent_id=None):
        self.name = name
        self.activation_key = activation_key
        self.parent_id = parent_id


def main():
    engine = create_engine("mysql://orlas:salro@localhost/orlas")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()


if __name__ == "__main__":
    main()
    #pass
