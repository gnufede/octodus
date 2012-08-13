# -*- coding: utf-8 -*-

from flask.ext.wtf import (Form, HiddenField, BooleanField, TextField, IntegerField,
                          PasswordField, SubmitField, TextField,DateTimeField,
                          ValidationError, required, equal_to, email,
                          length)
from flaskext.babel import gettext, lazy_gettext as _

from fbone.models import Session


class EditSessionForm(Form):
    next = HiddenField()
    begin = DateTimeField(_('Begin date'), [required()])
    end = DateTimeField(_('End date'), [required()])
    block_duration = IntegerField(_('Block duration'), [required()])
    block_capacity = IntegerField(_('Block capacity'), [required()])
    submit = SubmitField(_('Save'))

