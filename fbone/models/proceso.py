# -*- coding: utf-8 -*-

from fbone.extensions import db
from fbone.utils import get_current_time, VARCHAR_LEN_128
from sqlalchemy import Table, Column, Integer
from sqlalchemy.ext.declarative import declarative_base


class Page(db.Model):

    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    content = db.Column(db.UnicodeText(length=2000), nullable=False)


    def __repr__(self):
        return '%r' % self.content

