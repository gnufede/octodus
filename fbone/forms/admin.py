# -*- coding: utf-8 -*-

from flask.ext.wtf import (Form, HiddenField, BooleanField, TextField, FieldList,
                          PasswordField, SubmitField, TextField, SelectField, 
                          ValidationError, required, equal_to, email, Label, TextAreaField,
                          length)
from flaskext.babel import gettext, lazy_gettext as _

from fbone.extensions import db
from fbone.models import User, Project, Group

class EditProcesoForm(Form):
    next = HiddenField()
    textarea = TextAreaField()
    submit = SubmitField(_('Guardar'))

class NewGroupForm(Form):
    #types = Group.query(Group.type).distinct()
    next = HiddenField()
    parent = HiddenField()
    group_id = HiddenField()
  
    name = TextField("Nombre", [required()])
    #type = TextField("Tipo nuevo")
    activation_key = TextField(u"Codigo de activación", [required()])
    #choosetype = SelectField("Tipos existentes")
    choosetype = TextField("Tipos existentes")
   

    submit = SubmitField(_('Guardar'))

    
    def set_node (self, node):
        self.name.value = node.name
        self.choosetype.value = node.type
        self.activation_key.value = node.activation_key
        self.group_id.value = node.id

    def set_types (self, types):
        children = []
        for i in types:
            children.append((i[0], i[0]))
        self.choosetype.choices = children

      
    #def set_user_data(self, current_user):
    #    self.name.default = current_user.name

 #   def validate_email(self, field):
 #       if Group.query.filter_by(email=field.data).first() is None:
 #           raise ValidationError, gettext('This email is taken')




class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(_('Password'), [required(), length(min=6, max=16)])
    submit = SubmitField(_('Reauthenticate'))
