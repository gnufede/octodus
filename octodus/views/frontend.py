# -*- coding: utf-8 -*-

from uuid import uuid4
#from datetime import datetime

from flask import (Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, abort)
                   #Markup, g
from flaskext.mail import Message
from flaskext.babel import gettext as _
from flask.ext.login import (login_required, login_user, current_user,
                            logout_user, confirm_login,
                            login_fresh)
                            #fresh_login_required

from octodus.decorators import cached_response
from octodus.models import User, Project
from octodus.extensions import db, mail, login_manager  # cache
from octodus.forms import (SignupForm, LoginForm, RecoverPasswordForm,
                           TaskForm,
                         ChangePasswordForm, ReauthForm)
import os
import re
from werkzeug import check_password_hash  # generate_password_hash

frontend = Blueprint('frontend', __name__)


@frontend.route('/')
@cached_response
def index():
    if current_user.is_authenticated():
        return redirect(url_for('user.index'))
    else:
        return redirect(url_for('frontend.login'))

    login_form = signup_form = None
    if not current_user.is_authenticated():
        login_form = LoginForm(next=request.args.get('next'))
        signup_form = SignupForm(next=request.args.get('next'))
    page = int(request.args.get('page', 1))
    horario = "bla "
    pagination = User.query.paginate(page=page, per_page=10)
    return render_template('index.html', horario=horario,
                            newtaskform = TaskForm(),
                            pagination=pagination, login_form=login_form,
                           signup_form=signup_form, current_user=current_user)


@frontend.route('/email')
@cached_response
def email():
    login_form = LoginForm(next=request.args.get('next'))
    form = SignupForm(next=request.args.get('next'))
    return render_template('email.html', login_form=login_form,
                            newtaskform = TaskForm(),
                           signup_form=form, current_user=current_user)




@frontend.route('/search')
def search():
    login_form = None
    if not current_user.is_authenticated():
        login_form = LoginForm(next=request.args.get('next'))
    keywords = request.args.get('keywords', '').strip()
    pagination = None
    if keywords:
        page = int(request.args.get('page', 1))
        pagination = User.search(keywords).paginate(page, 1)
    else:
        pagination = None #User.query.all()
        flash('Please input keyword(s)', 'error')
    return render_template('search.html', pagination=None,
                            newtaskform = TaskForm(),
                           keywords=keywords, login_form=login_form)


@frontend.route('/login', methods=['GET', 'POST'])
def login():
   # email=request.args.get('email', 'tu_email@email.com')
    form = LoginForm(email=request.args.get('email', None),
                     next=request.args.get('next', None))
    tries = request.args.get('tries', 0)
    login_form = form
    if form.validate_on_submit():
        user, authenticated = User.authenticate(form.email.data,
                                    form.password.data)

        if user:
            if authenticated:
                remember = request.form.get('remember') == 'y'
                if login_user(user, remember=remember):
                    name = [user.username,user.name][bool(user.name)]
                    flash("Welcome, " + name + '!', 'success')
                         # Logged in!
                return redirect(form.next.data or url_for('user.index'))
            else:
                flash(_('Sorry, invalid login'), 'error')
                    # Sorry, invalid login
                tries = tries + 1

        else:
            flash(_('Sorry, there is no such account'), 'error')
                    #Sorry, there is no such account
            return redirect(url_for('frontend.signup', email=form.email.data))
    if form.email.data:
        return render_template('login.html', form=form, tries=tries, 
                                newtaskform = TaskForm(),
                                email=form.email.data, login_form=login_form)
    return render_template('login.html', form=form, tries=tries, 
                            newtaskform = TaskForm(),
                           login_form=login_form)
    #return redirect(url_for('frontend.login',email=email))


@frontend.route('/reauth', methods=['GET', 'POST'])
@login_required
def reauth():
    form = ReauthForm(next=request.args.get('next'))

    if request.method == 'POST':
        user, authenticated = User.authenticate(current_user.username,
                                    form.password.data)
        if user and authenticated:
            confirm_login()
            current_app.logger.debug('reauth: %s' % session['_fresh'])
            flash(_('Reauthenticate.'), 'success')  # Reauthenticate
            return redirect('/change_password')

        flash(_(u'Password is wrong.'), 'error') #Password is wrong.
    return render_template('reauth.html', 
                            newtaskform = TaskForm(),
                            form=form)


@frontend.route('/logout')
@login_required
def logout():
    if current_user:
        logout_user()
        flash(_('You are now logged out'), 'success')
                  # You are now logged out
    return redirect(url_for('frontend.index'))


@frontend.route('/signup', methods=['GET', 'POST'])
def signup():
    login_form = LoginForm(next=request.args.get('next'))
    form = SignupForm(next=request.args.get('next'),
                        email=request.args.get('email'),
                     code=request.args.get('code'))

    if form.validate_on_submit(): # or \
        #(request.method == 'POST' ):
#        (request.method == 'POST' and form.nocode.data):
        #if form.nocode.data:
        #    return redirect(url_for('frontend.email'))
        #else:
        if True:
           # activation_key = form.code.data
           # group = Project.query.\
           #         filter_by(activation_key=activation_key).first()
           # if group:
                user = User()
                form.populate_obj(user)
                user.activation_key = form.code.data
           #     group.users.append(user)
                user.points = 10
                inbox = Project(name='Inbox', owner=user)
                private = Project(name='Private', owner=user)
                public = Project(name='Public', owner=user)

                db.session.add(user)
                db.session.add(inbox)
                db.session.add(private)
                db.session.add(public)

                activation = re.compile('^'+user.activation_key+'$', re.I)
                for friend in User.query.all():
                    if activation.match(friend.username):
                        friend.points += 1
                        friend.follow(user)
                        user.follow(friend)

                db.session.commit()

                if login_user(user):
                    return redirect(form.next.data or url_for('user.index'))
           # else:
           #     flash(_("Codigo no valido"),
           #              #Invalid code
           #       "error")

    return render_template('signup.html', form=form,
                            newtaskform = TaskForm(),
                           login_form=login_form)


@frontend.route('/change_password', methods=['GET', 'POST'])
def change_password():
    user = None
    email = None
    if 'activation_key' in request.values and 'email' in request.values:
        activation_key = request.values['activation_key']
        email = request.values['email']
        session['activation_key'] = activation_key
        session['email'] = email
        user = User.query.filter_by(activation_key=activation_key) \
                         .filter_by(email=email).first()
    elif current_user.is_authenticated():
        if not login_fresh():
            return login_manager.needs_refresh()
        user = current_user
    else:
        if 'email' and 'activation_key' in session:
            email = session['email']
            activation_key = session['activation_key']
            user = User.query.filter_by(activation_key=activation_key) \
                         .filter_by(email=email).first()

    if not user:
        abort(403)

    form = ChangePasswordForm(activation_key=user.activation_key)
    if form.validate_on_submit():
        user.password = form.password.data
        user.activation_key = None
        db.session.add(user)
        db.session.commit()

        session.pop('email', None)
        session.pop('activation_code', None)
        if current_user.is_authenticated():
            flash(_(u"Your password has been changed, please log in again"),
                    #Your password has been changed, please log in again
              "success")
            return redirect(url_for("user.index", email=email))
        else:
            flash(_(u"Your password has been changed, please log in again"),
                 #Your password has been changed, please log in again
              "success")
            return redirect(url_for("frontend.login", email=email))

    return render_template("change_password.html",
                            newtaskform = TaskForm(),
                           form=form)


@frontend.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = RecoverPasswordForm()

    if 'value' in request.values:
        value = request.values['value']
    else:
        value = ''

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash(_('Please see your email for instructions on '
                  'how to access your account'
                   ), 'success')
            user.activation_key = str(uuid4())
            db.session.add(user)
            db.session.commit()
            body = render_template('emails/reset_password.html', user=user)
            message = Message(subject=_('Recover your password'), html=body,
                              recipients=[user.email])
            mail.send(message)

            return redirect(url_for('frontend.index'))
        else:
            flash(_('Sorry, no user found for that email address'),
                    'error')  # Sorry, no user found for that email address

    return render_template('reset_password.html',
                            newtaskform = TaskForm(),
                           form=form, value=value)




@frontend.route('/about')
def about():
    return '<h1>About Page</h1>'


@frontend.route('/blog')
def blog():
    return '<h1>Blog Page</h1>'


@frontend.route('/help')
def help():
    return '<h1>Help Page</h1>'


@frontend.route('/terms')
def terms():
    return '<h1>Terms Page</h1>'
