# -*- coding: utf-8 -*-

from fbone.extensions import db
from fbone.models import DenormalizedText
from fbone.utils import get_current_time, VARCHAR_LEN_128
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


class Group(db.Model):

    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(VARCHAR_LEN_128), nullable=False, unique=True)
    activation_key = db.Column(db.String(VARCHAR_LEN_128), nullable=False, unique=True)
    created_time = db.Column(db.DateTime, default=get_current_time)
    parent = db.Column(db.Integer)

    def __repr__(self):
        return '<Group %r>' % self.name

