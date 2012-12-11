# -*- coding: utf-8 -*-

from flask.ext.wtf import (Form, HiddenField, BooleanField, TextField,
                          PasswordField, SubmitField,
                          ValidationError, required, equal_to, email,
                          length)
from flaskext.babel import gettext, lazy_gettext as _

from octodus.models import User


class LoginForm(Form):
    next = HiddenField()
    remember = BooleanField(_(u'Remember me'))  # Remember me
    email = TextField(_(u'Username / Email'), [required()])
                # Username or email address
    password = PasswordField(_(u'Password'), [required(),
        length(min=6, max=56)])  # Password
    submit = SubmitField(_(u'Login'))  # Login


class SignupForm(Form):
    next = HiddenField()
    code = TextField(_(u'Code'), [required()]) # Code
    username = TextField(_(u'Username'), [required()])  # Username
    password = PasswordField(u'Password',  # Password
        [required(), length(min=8, max=56)])
    password_again = PasswordField(_(u'Password again'),  # Password again
        [required(), equal_to('password')])
    email = TextField(_(u'Email'), [required(), email(
        message=_(u"A valid email address is required"))])
        # Email address  # A valid email address is required
    #nocode = BooleanField(_(u'No tengo código para registrarme'))
    submit = SubmitField(_(u'Signup'))  # Signup

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError, gettext(u'This email is already registered')
            #This email is taken

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError, gettext(u'This username is already registered')
            #This email is taken


class RecoverPasswordForm(Form):
    email = TextField(_(u'Your email'), validators=[  # Your email
                      email(message=_(u'A valid email address is required'))])
                      #A valid email address is required
    submit = SubmitField(_(u'Send instructions'))  # Send instructions


class ChangePasswordForm(Form):
    activation_key = HiddenField()
    password = PasswordField(u'Password', validators=[required(message=_(
        u'At least 8 characters')),
        #Password is required
        length(min=8, max=56)])
    password_again = PasswordField(_(u'Password again'), validators=[
        #Password again
        equal_to('password', message=
        _(u"Passwords don't match")), required()])  # Passwords don't match
    submit = SubmitField(_(u'Save'))  # Save


class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(_(u'Password'), [required(),
        length(min=8, max=56)])  # Password
    submit = SubmitField(_(u'Reauthenticate'))  # Reauthenticate


