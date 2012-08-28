# -*- coding: utf-8 -*-

from flask.ext.wtf import (Form, HiddenField, BooleanField, TextField, IntegerField,
                          PasswordField, SubmitField, TextField,DateTimeField,
                          ValidationError, required, equal_to, email,
                          length)
from flaskext.babel import gettext, lazy_gettext as _

from fbone.models import Session
import dateutil.parser

class EditSessionForm(Form):
    next = HiddenField()
    #date = DateTimeField(_('Fecha'), [required()])
    #begin = DateTimeField(_('Hora de inicio'), [required()])
    #end = DateTimeField(_('Hora de fin'), [required()])
    start_date = TextField(_('Fecha de inicio'), [required()])
    end_date = TextField(_('Fecha de fin'), [required()])
    time_begin = TextField(_('Hora de inicio'), [required()])
    time_end = TextField(_('Hora de fin'), [required()])
    block_duration = IntegerField(_(u'Duración del bloque (minutos)'), [required()])
    block_capacity = IntegerField(_(u'Personas por bloque'), [required()])
    submit = SubmitField(_('Guardar'))

    def validate_dates(self, field):
       start_date = dateutil.parser.parse(field.start_date) 
       end_date = dateutil.parser.parse(field.end_date) 
       if (end_date-begin_date).days < 0:
           raise ValidationError, gettext(u'La fecha de fin debe ser posterior a la de inicio')
       
    def validate_time(self, field):
       start_time = dateutil.parser.parse(field.time_begin) 
       end_time = dateutil.parser.parse(field.time_end) 
       if (end_time-begin_time).seconds < 61:
           raise ValidationError, gettext(u'La hora de fin debe ser posterior a la de inicio')

