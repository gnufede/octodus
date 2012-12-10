# -*- coding: utf-8 -*-

from flask.ext.wtf import (Form, HiddenField, BooleanField, TextField,
                          PasswordField, SubmitField,
                          ValidationError, required, equal_to, email,
                          length)
from flaskext.babel import gettext, lazy_gettext as _

from octodus.models import User


class LoginForm(Form):
    next = HiddenField()
    remember = BooleanField(_(u'Recuérdame'))  # Remember me
    email = TextField(_(u'Username / Dirección de email'), [required()])
                # Username or email address
    password = PasswordField(_(u'Contraseña'), [required(),
        length(min=6, max=56)])  # Password
    submit = SubmitField(_(u'Entrar'))  # Login


class SignupForm(Form):
    next = HiddenField()
    code = TextField(_(u'Código'), [required()]) # Code
    username = TextField(_(u'Username'), [required()])  # Username
    password = PasswordField(u'Contraseña',  # Password
        [required(), length(min=8, max=56)])
    password_again = PasswordField(_(u'Contraseña otra vez'),  # Password again
        [required(), equal_to('password')])
    email = TextField(_(u'Dirección de email'), [required(), email(
        message=_(u'Vamos a informarte vía emails, danos el tuyo por favor'))])
        # Email address  # A valid email address is required
    #nocode = BooleanField(_(u'No tengo código para registrarme'))
    submit = SubmitField(_(u'Registrarse'))  # Signup

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError, gettext(u'Este email ya está registrado')
            #This email is taken


class RecoverPasswordForm(Form):
    email = TextField(_(u'Tu email'), validators=[  # Your email
                      email(message=_(u'Se requiere un email válido'))])
                      #A valid email address is required
    submit = SubmitField(_(u'Enviar instrucciones'))  # Send instructions


class ChangePasswordForm(Form):
    activation_key = HiddenField()
    password = PasswordField(u'Contraseña', validators=[required(message=_(
        u'Se requiere una contraseña de al menos 6 caracteres')),
        #Password is required
        length(min=8, max=56)])
    password_again = PasswordField(_(u'Contraseña otra vez'), validators=[
        #Password again
        equal_to('password', message=
        _(u'Las contraseñas deben ser la misma')), required()])  # Passwords don't match
    submit = SubmitField(_(u'Guardar'))  # Save


class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(_(u'Contraseña'), [required(),
        length(min=8, max=56)])  # Password
    submit = SubmitField(_(u'Reautenticarse'))  # Reauthenticate


