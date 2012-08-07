# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, g, redirect, url_for, request
from flask.ext.login import login_required, current_user

from fbone.models import User
from fbone.decorators import keep_login_url
from fbone.forms import (EditDatosForm)


user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/')
@login_required
def index():
    return render_template('user_index.html', current_user=current_user)

@user.route('/edit_datos')
@login_required
def edit_datos():
    form = EditDatosForm(next=request.args.get('next'),current_user=current_user)
    return render_template('user_edit_datos.html', form=form,
                           current_user=current_user)


@user.route('/<name>')
def pub(name):
    if current_user.is_authenticated() and current_user.name == name:
        return redirect(url_for('user.index'))

    user = User.query.filter_by(name=name).first_or_404()
    return render_template('user_pub.html', user=user)
