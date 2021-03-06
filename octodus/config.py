# -*- coding: utf-8 -*-
import os

APP_NAME = 'octodus'


class BaseConfig(object):

    DEBUG = False
    TESTING = True

    # os.urandom(24)
    SECRET_KEY = 'w\xcb?\x00\xdf\x16_\x11\xb5+\xce\xdc\xa3\xf1\xa3\xa3X\x1d\t\xe5\x19\xbb=\xe4'


class DefaultConfig(BaseConfig):

    SQLALCHEMY_ECHO = True

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://octodus:sudotco@localhost/octodus'

    if os.environ.get('SHARED_DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('SHARED_DATABASE_URL')
        DEBUG = False
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        DEBUG = False
        #'mysql://51828:EFDOtest;;@mysql2.alwaysdata.com/efdigitalorlas_orlas'

    # Sqlite
#    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/octodus.db'
    # Mysql: 'mysql://dbusername:dbpassword@dbhost/dbname'

    # To create log folder.
    # $ sudo mkdir -p /var/log/octodus
    # $ sudo chown $USER /var/log/octodus
    DEBUG_LOG = '/tmp/octodus-debug.log'

    ACCEPT_LANGUAGES = ['es', 'en']
    BABEL_DEFAULT_LOCALE = 'es'

    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 60

    # Email (Flask-email)
    # https://bitbucket.org/danjac/flask-mail/issue/3/problem-with-gmails-smtp-server
    MAIL_DEBUG = DEBUG
    MAIL_SERVER = 'smtp.webfaction.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'efdigital'
    MAIL_PASSWORD = 'a0e11dbe'
    #DEFAULT_MAIL_SENDER = '%s@mail.webfaction.com' % MAIL_USERNAME
    DEFAULT_MAIL_SENDER = 'efdigital@efdigitalorlas.com'

    TESTING = False
    #TESTING = True


class TestConfig(BaseConfig):
    TESTING = True
    CSRF_ENABLED = False

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
