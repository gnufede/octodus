# -*- coding: utf-8 -*-

import os
from flask_gzip import Gzip

from flask import Flask, request, render_template
from flaskext.babel import Babel
from flaskext.gravatar import Gravatar


from octodus import utils
from octodus.models import User
from octodus.config import DefaultConfig, APP_NAME
from octodus.views import frontend, user, api, admin
from octodus.extensions import db, mail, cache, login_manager


# For import *
__all__ = ['create_app']

DEFAULT_BLUEPRINTS = (
    frontend,
    user,
    api,
    admin,
)

import types
def is_list(obj):
    return isinstance(obj, types.ListType)



def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = APP_NAME
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name)
    configure_app(app, config)
    configure_hook(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    #configure_logging(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    app.jinja_env.tests['is_list'] = is_list
    app.jinja_env.filters['type'] = type
    gravatar = Gravatar(app,
                    size=60,
                    rating='g',
                    default='mm',
                    force_default=False,
                    force_lower=False)
    gzipped = Gzip(app)
    app = gzipped.app

    return app


def configure_app(app, config):
    """Configure app from object, parameter and env."""

    app.config.from_object(DefaultConfig)
    if config is not None:
        app.config.from_object(config)
    # Override setting by env var without touching codes.
    app.config.from_envvar('octodus_APP_CONFIG', silent=True)


def configure_extensions(app):
    # sqlalchemy
    db.init_app(app)
    # mail
    mail.init_app(app)
    # cache
    cache.init_app(app)

    # babel
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        #accept_languages = app.config.get('ACCEPT_LANGUAGES')
        return request.accept_languages.best_match(['es', 'en'])
    from flaskext.babel import refresh; refresh()

    # login.
    login_manager.login_view = 'frontend.login'
    login_manager.refresh_view = 'frontend.reauth'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    login_manager.init_app(app)


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_template_filters(app):
    @app.template_filter()
    def pretty_date(value):
        return utils.pretty_date(value)


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

  #  if app.debug or app.testing:
        # skip debug and test mode.
  #      return

    import logging
    from logging.handlers import SMTPHandler  # , RotatingFileHandler

    # Set info level on logger, which might be overwritten by handers.
    app.logger.setLevel(logging.INFO)

    debug_log = os.path.join(app.root_path, app.config['DEBUG_LOG'])
    file_handler = logging.handlers.RotatingFileHandler(debug_log,
                        maxBytes=100000, backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(file_handler)

    ADMINS = ['gnu.fede@gmail.com']
    mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                               app.config['MAIL_USERNAME'],
                               ADMINS,
                               'O_ops... octodus failed!',
                               (app.config['MAIL_USERNAME'],
                                app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(mail_handler)


def configure_hook(app):
    @app.before_request
    def before_request():
        pass
  #  @app.after_request
  #  def after_request(response):
  #      return app.gzip.after_request(response)


def configure_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/forbidden_page.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/page_not_found.html"), 404

    @app.errorhandler(405)
    def method_not_allowed_page(error):
        return render_template("errors/method_not_allowed.html"), 405

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/server_error.html"), 500
