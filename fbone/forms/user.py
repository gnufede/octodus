# -*- coding: utf-8 -*-

from flask.ext.wtf import (Form, HiddenField, BooleanField, TextField, FieldList,
                          PasswordField, SubmitField, TextField, SelectField, 
                          ValidationError, required, equal_to, email, Label,
                          RadioField, SelectMultipleField, length)
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
    surname = TextField(_('Apellidos'), [required()])
    name = TextField(_('Nombre'), [required()])
    projects = FieldList(TextField(""))
    nextproject = SelectField("")
    incorrect = BooleanField(u'Mi carrera/especialidad/grupo no sale en la lista')

    submit = SubmitField(_('Guardar'))
    
    
    def validate_nextproject(self, field):
        if Project.query.filter_by(id=field.data).first() is None:
            raise ValidationError, gettext('Ese grupo no existe')

    

    def generate_groups (self, groups):
        for idx, val in enumerate(groups):
            self.projects.append_entry(TextField(val.type))
            self.projects[idx].label = Label('projects-'+str(idx),val.type)
            if val.children:
                children = []
                types_list = []
                for i in val.children:
                    children.append((i.id, "("+i.type+") " + i.name))
                    types_list.append(i.type)
                types_set = list(set(types_list))
                types_label = str(types_set[0])
                for i in types_set[1:]:
                    types_label = types_label +'/'+ i
                self.nextproject.choices = children
                self.nextproject.label = Label('projects-'+str(idx+1),types_label)
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


class UserAppointmentForm(Form):
    next = HiddenField()
    session = HiddenField()
    hour = RadioField(_('Hora'))
    submit = SubmitField(_('Confirmar'))

    def set_hours(self, hours):
        self.hour.choices = hours

class UserOfferForm(Form):
    next = HiddenField()
    options = RadioField(_('Oferta'))
    submit = SubmitField(_('Continuar'))
    type = HiddenField()

    def set_offer_type(self, type):
        self.type.data = type

class UserPollForm(Form):
    next = HiddenField()
    options = RadioField(_(u'Elección'))
    submit = SubmitField(_('Continuar'))
    type = HiddenField()

    def set_poll_type(self, type):
        self.type.data = type
