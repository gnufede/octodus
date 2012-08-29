# -*- coding: utf-8 -*-

from uuid import uuid4
from datetime import datetime

from flask import (Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, g, abort, Markup)
from flaskext.mail import Message
from flaskext.babel import gettext as _
from flask.ext.login import (login_required, login_user, current_user,
                            logout_user, confirm_login, fresh_login_required,
                            login_fresh)

from fbone.decorators import cached_response
from fbone.models import User, Proceso, Project
from fbone.extensions import db, cache, mail, login_manager
from fbone.forms import (SignupForm, LoginForm, RecoverPasswordForm,
                         ChangePasswordForm, ReauthForm)


frontend = Blueprint('frontend', __name__)


@frontend.route('/')
@cached_response
def index():
    if current_user.is_authenticated():
        return redirect(url_for('user.index'))

    login_form = signup_form = None
    if not current_user.is_authenticated():
        login_form= LoginForm(next=request.args.get('next'))
        signup_form = SignupForm(nex=request.args.get('next'))
    page = int(request.args.get('page', 1))
    pagination = User.query.paginate(page=page, per_page=10)
    return render_template('index.html', pagination=pagination, login_form=login_form,
                           signup_form=signup_form, current_user=current_user)


@frontend.route('/search')
def search():
    login_form = None
    if not current_user.is_authenticated():
        login_form= LoginForm(next=request.args.get('next'))
    keywords = request.args.get('keywords', '').strip()
    pagination = None
    if keywords:
        page = int(request.args.get('page', 1))
        pagination = User.search(keywords).paginate(page, 1)
    else:
        pagination = User.query.all()
        flash('Please input keyword(s)', 'error')
    return render_template('search.html', pagination=pagination,
                           keywords=keywords, login_form=login_form)


@frontend.route('/login', methods=['GET', 'POST'])
def login():
   # email=request.args.get('email', 'tu_email@email.com')
    form = LoginForm(email=request.args.get('email', None),
                     next=request.args.get('next', None))
    
    
    tries = request.args.get('tries', 0)
    if form.validate_on_submit():
        user, authenticated = User.authenticate(form.email.data,
                                    form.password.data)

        if user: 
            if authenticated:
                remember = request.form.get('remember') == 'y'
                if login_user(user, remember=remember):
                    flash("Bienvenido, "+user.name+'!', 'success') # Logged in!
                return redirect(form.next.data or url_for('user.index'))
            else:
                flash(_('Vaya, no es correcto'), 'error') # Sorry, invalid login
                tries = tries + 1

        else:
            flash(_('Lo sentimos, esa cuenta no existe'), 'error') #Sorry, there is no such account
            return redirect(url_for('frontend.signup',email=form.email.data))
    if form.email.data:
        return render_template('login.html', form=form, tries=tries, email=form.email.data)
    return render_template('login.html', form=form, tries=tries)
    #return redirect(url_for('frontend.login',email=email))


@frontend.route('/reauth', methods=['GET', 'POST'])
@login_required
def reauth():
    form = ReauthForm(next=request.args.get('next'))

    if request.method == 'POST':
        user, authenticated = User.authenticate(current_user.name,
                                    form.password.data)
        if user and authenticated:
            confirm_login()
            current_app.logger.debug('reauth: %s' % session['_fresh'])
            flash(_('Reautenticado.'), 'success') #Reauthenticate
            return redirect('/change_password')

        flash(_(u'La contraseña no es correcta.'), 'error') #Password is wrong.
    return render_template('reauth.html', form=form)


@frontend.route('/logout')
@login_required
def logout():
    if current_user:
        logout_user()
        flash(_('Has salido correctamente'), 'success') #You are now logged out
    return redirect(url_for('frontend.index'))


@frontend.route('/signup', methods=['GET', 'POST'])
def signup():
    login_form= LoginForm(next=request.args.get('next'))
    form = SignupForm(next=request.args.get('next'), email=request.args.get('email'))

    if form.validate_on_submit():
       
        activation_key = form.code.data
        group = Project.query.filter_by(activation_key=activation_key).first()
        if group:
            user = User()
            form.populate_obj(user)            
            group.users.append(user)

            db.session.add(user)
            
            db.session.commit()

            if login_user(user):
                return redirect(form.next.data or url_for('user.index'))
        else:
            flash(_("Codigo no valido"), #Invalid code
              "error")

    return render_template('signup.html', form=form, login_form=login_form)


@frontend.route('/change_password', methods=['GET', 'POST'])
def change_password():
    user = None
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

        flash(_("Se ha cambiado tu contraseña, por favor, entra otra vez"), #Your password has been changed, please log in again
              "success")
        session.pop('email', None)
        session.pop('activation_code', None)
        return redirect(url_for("frontend.login",email=email))
  
    return render_template("change_password.html", form=form)



@frontend.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = RecoverPasswordForm()

    if 'value' in request.values:
        value = request.values['value']
    else: value = ''

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash(_('Sigue las indicaciones que hemos enviado a tu correo '
                  'para acceder a tu cuenta'), 'success') #Please see your email for instructions on
                                                            #how to access your account
            user.activation_key = str(uuid4())
            db.session.add(user)
            db.session.commit()
            body = render_template('emails/reset_password.html', user=user)
            message = Message(subject=_('Recover your password'), html=body,
                              recipients=[user.email])
            mail.send(message)

            return redirect(url_for('frontend.index'))
        else:
            flash(_('Lo sentimos, no hay ningún usuario con esa dirección'), 'error') #Sorry, no user found for that email address

    return render_template('reset_password.html', form=form, value=value)

@frontend.route('/proceso')
@cached_response
def proceso():
    login_form = form = None
    if not current_user.is_authenticated():
        login_form= LoginForm(next=request.args.get('next'))
        form = SignupForm(next=request.args.get('next'))
    proceso = Proceso.query.first()
    return render_template('proceso.html', proceso=proceso.content,
                       login_form=login_form,
                           form=form)



@frontend.route('/edit_session')
def edit_session():
    user = current_user
    if not user or not user.is_admin() or not user.is_coordinator():
        abort(403)
    
    proceso = Proceso.query.first()
    return render_template('edit_proceso.html', proceso=proceso.content)





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
