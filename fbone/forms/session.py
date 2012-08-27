# -*- coding: utf-8 -*-

from flask.ext.wtf import (Form, HiddenField, BooleanField, TextField, IntegerField,
                          PasswordField, SubmitField, TextField,DateTimeField,
                          ValidationError, required, equal_to, email,
                          length)
from flaskext.babel import gettext, lazy_gettext as _

from fbone.models import Session


class EditSessionForm(Form):
    next = HiddenField()
    #date = DateTimeField(_('Fecha'), [required()])
    #begin = DateTimeField(_('Hora de inicio'), [required()])
    #end = DateTimeField(_('Hora de fin'), [required()])
    date = TextField(_('Fecha'), [required()])
    begin = TextField(_('Hora de inicio'), [required()])
    end = TextField(_('Hora de fin'), [required()])
    block_duration = IntegerField(_(u'Duración del bloque (minutos)'), [required()])
    block_capacity = IntegerField(_(u'Personas por bloque'), [required()])
    submit = SubmitField(_('Guardar'))

