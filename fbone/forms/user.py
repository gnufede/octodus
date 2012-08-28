# -*- coding: utf-8 -*-

from flask.ext.wtf import (Form, HiddenField, BooleanField, TextField, FieldList,
                          PasswordField, SubmitField, TextField, SelectField, 
                          ValidationError, required, equal_to, email, Label,
                          length)
from flaskext.babel import gettext, lazy_gettext as _

from fbone.models import User, Project

class EditDateForm(Form):
    next = HiddenField()
#    date = DateTimeField()
    date = SelectField("Fecha de la cita")

    submit = SubmitField(_('Save'))

    def generate_dates (self, dates):
        form_dates = []
        for i in dates:
            form_dates.append((i.id, i.begin))
        self.date.choices = form_dates
     

class EditDatosForm(Form):
    next = HiddenField()
    surname = TextField(_('Surname'), [required()])
    name = TextField(_('Name'), [required()])
    projects = FieldList(TextField(""))
    nextproject = SelectField("")

    submit = SubmitField(_('Save'))
    
    
    def validate_nextproject(self, field):
        if Project.query.filter_by(id=field.data).first() is None:
            raise ValidationError, gettext('This group does not exist')

    

    def generate_groups (self, groups):
        for idx, val in enumerate(groups):
            self.projects.append_entry(TextField(val.type))
            self.projects[idx].label = Label('projects-'+str(idx),val.type)
            if val.children:
                self.nextproject.label = Label('projects-'+str(idx+1),val.children[0].type)
                children = []
                for i in val.children:
                    children.append((i.id, i.name))
                self.nextproject.choices = children
            else:
                del self.nextproject
     
            
    #def set_user_data(self, current_user):
    #    self.name.default = current_user.name

 #   def validate_email(self, field):
 #       if Group.query.filter_by(email=field.data).first() is None:
 #           raise ValidationError, gettext('This email is taken')




class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(_('Password'), [required(), length(min=6, max=16)])
    submit = SubmitField(_('Reauthenticate'))
