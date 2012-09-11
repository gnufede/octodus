# -*- coding: utf-8 -*-
import os

APP_NAME = 'fbone'

class BaseConfig(object):

    DEBUG = False
    TESTING = True

    # os.urandom(24)
    SECRET_KEY = 'secret key'


class DefaultConfig(BaseConfig):

    SQLALCHEMY_ECHO = True

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://orlas:salro@localhost/orlas'

    if os.environ.get('SHARED_DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = 'mysql://51828:EFDOtest;;@mysql2.alwaysdata.com/efdigitalorlas_orlas'
        DEBUG = False

    # Sqlite
#    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/fbone.db'
    # Mysql: 'mysql://dbusername:dbpassword@dbhost/dbname'

    # To create log folder.
    # $ sudo mkdir -p /var/log/fbone
    # $ sudo chown $USER /var/log/fbone
    DEBUG_LOG = '/tmp/fbone-debug.log'

    ACCEPT_LANGUAGES = ['en']
    BABEL_DEFAULT_LOCALE = 'es_ES'

    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 60

    # Email (Flask-email)
    # https://bitbucket.org/danjac/flask-mail/issue/3/problem-with-gmails-smtp-server
    MAIL_DEBUG = DEBUG
    MAIL_SERVER = 'smtp.webfaction.com'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'efdigital'
    MAIL_PASSWORD = 'a0e11dbe'
    DEFAULT_MAIL_SENDER = '%s@mail.webfaction.com' % MAIL_USERNAME


class TestConfig(BaseConfig):
    TESTING = True
    CSRF_ENABLED = False

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
