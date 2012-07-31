# -*- coding: utf-8 -*-

from fbone.extensions import db
from fbone.models import DenormalizedText
from fbone.utils import get_current_time, VARCHAR_LEN_128
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UsersGroups(db.Model):
    __tablename__ = 'users_groups'
    user_id = Column(db.Integer, ForeignKey('users.id'), primary_key=True)
    group_id = Column(db.Integer, ForeignKey('groups.id'), primary_key=True)
    extra_data = Column(db.String(VARCHAR_LEN_128))
    group = relationship("Group", backref="user_assoc")
    
    def __repr__(self):
        return '<User_groups %r>' % self.extra_data