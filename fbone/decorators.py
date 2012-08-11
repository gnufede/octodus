# -*- coding: utf-8 -*-

from functools import wraps

from flask import g, url_for, flash, redirect, Markup, request
from flaskext.babel import gettext as _


def keep_login_url(func):
    """
    Adds attribute g.keep_login_url in order to pass the current
    login URL to login/signup links.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.keep_login_url = True
        return func(*args, **kwargs)
    return wrapper


def cached_response(func):
    """
    Adds cache-control: public to responses
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        resp.cache_control.public = True
        return resp
    return wrapper
