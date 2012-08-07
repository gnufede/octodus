# -*- coding: utf-8 -*-

from flask.ext.wtf import (Form, HiddenField, BooleanField, TextField,
                          PasswordField, SubmitField, TextField,
                          ValidationError, required, equal_to, email,
                          length)
from flaskext.babel import gettext, lazy_gettext as _

from fbone.models import User


class EditDatosForm(Form, current_user=None):
    next = HiddenField()
    surname = TextField(_('Surname'), [required()], default=current_user.surname)
    name = TextField(_('Name'), [required()], default=current_user.name)
    university = TextField(_('University'), [required()])
    title = TextField(_('Title'), [required()])
    specialty = TextField(_('Specialty'))
    group = TextField(_('Group'))
    submit = SubmitField(_('Save'))


 #   def validate_email(self, field):
 #       if Group.query.filter_by(email=field.data).first() is None:
 #           raise ValidationError, gettext('This email is taken')




class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(_('Password'), [required(), length(min=6, max=16)])
    submit = SubmitField(_('Reauthenticate'))
