# -*- coding: utf-8 -*-

from flask.ext.wtf import (Form, HiddenField, BooleanField, TextField,
                          PasswordField, SubmitField, TextField,
                          ValidationError, required, equal_to, email,
                          length)
from flaskext.babel import gettext, lazy_gettext as _

from fbone.models import Session


class EditSessionForm(Form):
    next = HiddenField()
    begin = TextField(_('Begin date'), [required()])
    end = TextField(_('End date'), [required()])
    block_duration = TextField(_('Block duration'), [required()])
    block_capacity = TextField(_('Block capacity'), [required()])
    submit = SubmitField(_('Save'))

