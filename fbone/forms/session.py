# -*- coding: utf-8 -*-

from flask.ext.wtf import (Form, HiddenField, BooleanField, TextField, IntegerField,
                          PasswordField, SubmitField, TextField,DateTimeField,
                          ValidationError, required, equal_to, email,
                          length)
from flaskext.babel import gettext, lazy_gettext as _

from fbone.models import Session


class EditSessionForm(Form):
    next = HiddenField()
    date = DateTimeField(_('Fecha'), [required()])
    begin = DateTimeField(_('Hora de inicio'), [required()])
    end = DateTimeField(_('Hora de fin'), [required()])
    block_duration = IntegerField(_('Block duration'), [required()])
    block_capacity = IntegerField(_('Block capacity'), [required()])
    submit = SubmitField(_('Save'))

