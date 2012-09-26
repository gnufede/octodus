##!/usr/bin/env python
# -*- coding: utf-8 -*-


from fbone.extensions import db
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from flask import url_for

import datetime

from werkzeug import (generate_password_hash, check_password_hash, cached_property)
from flask.ext.login import UserMixin

#from flask import jsonify


class Definitions(object):
    USER_TYPE_ADMIN = 1
    USER_TYPE_COORDINATOR = 2
    

nodes_professors = db.Table("nodes_professors", db.metadata,
    db.Column("node_id", db.Integer, ForeignKey("nodes.id")),
    db.Column("professor_id", db.Integer, ForeignKey("professors.id")))


projects_users = db.Table("projects_users", db.metadata,
    db.Column("project_id", db.Integer, ForeignKey("projects.id")),
    db.Column("user_id", db.Integer, ForeignKey("users.id")))

projects_sessions = db.Table("projects_sessions", db.metadata,
    db.Column("project_id", db.Integer, ForeignKey("projects.id")),
    db.Column("session_id", db.Integer, ForeignKey("sessions.id")))

projects_offers = db.Table("projects_offers", db.metadata,
    db.Column("project_id", db.Integer, ForeignKey("projects.id")),
    db.Column("offer_id", db.Integer, ForeignKey("offers.id")),
    db.Column("overriden_price", db.Float))

class Act(db.Model):
    __tablename__ = "acts"
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(128), unique=True)
    password_hash = db.Column(db.String(256), unique=True)

class OfferSelection(db.Model):
    __tablename__ = "offers_users"
    project_id = db.Column(db.Integer, ForeignKey("projects.id"), primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"), primary_key=True)
    offer_id = db.Column(db.Integer, ForeignKey("offers.id"), primary_key=True)
    offer_type = db.Column(db.Integer, ForeignKey("offers.type"), primary_key=True)
    date = db.Column(db.DateTime, default=db.func.now())
    project = relationship("Project", backref=backref("offer_selection",cascade="all,delete,delete-orphan"))
    user = relationship("User", backref=backref("offer_selection",cascade="all,delete,delete-orphan"))
    offer = relationship("Offer", primaryjoin="Offer.id==OfferSelection.offer_id", backref=backref('offer_selection', cascade='all,delete,delete-orphan'))

class Offer(db.Model):
    __tablename__ = "offers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.String(128))
    #price = db.Column(db.Float())
    price = db.Column(db.Numeric(6, 2))
    picture = db.Column(db.String(128))
    type = db.Column(db.Integer, nullable=False, index=True)
    default = db.Column(db.Integer)
    depth = db.Column(db.Integer)
    parent_id = db.Column(db.Integer, ForeignKey("offers.id"))
    children = relationship("Offer",
                backref=backref('parent', remote_side=[id])
               )

    def jsonify(self):
        return {'id': self.id, 'name': self.name, 'children': [x.jsonify() for x in self.children]    }

    def jsonify_full(self):
        if self.price:
            jprice = str(self.price)
        else:
            jprice = 'N/A'
        return {'id': self.id, 'name': self.name, 'img': url_for('static', filename="offers/"+self.picture), 'description': self.description, 'price': jprice, 'children': [x.jsonify() for x in self.children]    }

class Appointment(db.Model):
    __tablename__ = "appointments"
    project_id = db.Column(db.Integer, ForeignKey("projects.id"), primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"), primary_key=True)
    session_id = db.Column(db.Integer, ForeignKey("sessions.id"), primary_key=True)
    date = db.Column(db.DateTime)
    project = relationship("Project", backref=backref("appointments",cascade="all,delete,delete-orphan"))
    user = relationship("User", backref=backref("appointments",cascade="all,delete,delete-orphan"))
    session = relationship("Session", backref=backref('appointments', cascade='all,delete,delete-orphan'))
    
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
    creation = db.Column(db.DateTime, default=db.func.now())
    users = relationship("User", secondary=projects_users, backref="projects")
    sessions = relationship("Session", secondary=projects_sessions, backref="projects")
    offers = relationship("Offer", secondary=projects_offers, backref="projects")
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
    def project_already_created(self,activation_key):
        return len(db.session.query(Project).filter(Project.activation_key==activation_key).all())
        
    def create(self, node):
        activation_key = node.activation_key + self.term
        new_project = db.session.query(Project).filter(Project.activation_key==activation_key).first()
        if not new_project:
            new_project = Project(term=self.term)
            new_project.name = node.name
            new_project.type = node.type
            new_project.activation_key = node.activation_key + self.term
            new_project.depth = node.depth
        if node.parent:
            parent_activation_key = node.parent.activation_key + self.term
            parent_project = db.session.query(Project).filter(Project.activation_key==parent_activation_key).first()
            if parent_project:
                parent_project.children.append(new_project)
            else:
                self.children.append(new_project)
        else:
            self.children.append(new_project)
        db.session.commit()
        for j in node.children:
            new_project.create(j)

    def set_offer(self, offer):
        if self.children:
            for j in self.children:
                j.set_offer(offer)
        if offer not in self.offers:
            self.offers.append(offer)
            db.session.commit()

    def remove_offer(self, offer):
        if self.children:
            for j in self.children:
                j.remove_offer(offer)
        if offer in self.offers:
            self.offers.remove(offer)

    def set_session(self, session):
        if self.children:
            for j in self.children:
                j.set_session(session)
        else:
            self.sessions.append(session)
            db.session.commit()
    
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

    def jsonify_OLD(self):
        children = dict()
        if len(self.children) >= 1:
            for val in self.children:
                #children.append(val.jsonify)
                children[val.id] = val.jsonify()
        return {'name':self.name, 'children':children}
    
    def jsonify(self):
        #return "{'name':%s, 'id':%d, 'children':%s}" % (self.name, self.id, repr([x.jsonify() for x in self.children]))
        #return jsonify(name=self.name, id=self.id, children=str([x.jsonify() for x in self.children]))
        return {'id': self.id, 'name': self.name, 'children': [x.jsonify() for x in self.children]}
        
#    def __init__(self, begin, end, parent_id=None):
#        self.name = name
#        self.activation_key = activation_key
#        self.parent_id = parent_id




#def main():
#    engine = create_engine("mysql://efdigital_orlas:salro@localhost/efdigital_orlas")
#    Base.metadata.create_all(engine)
#    Session = sessionmaker(bind=engine)
#    session = Session()


#if __name__ == "__main__":
#    #main()
#    pass
