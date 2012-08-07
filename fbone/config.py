# -*- coding: utf-8 -*-
import os

APP_NAME = 'fbone'

class BaseConfig(object):

    DEBUG = False
    TESTING = False

    # os.urandom(24)
    SECRET_KEY = 'secret key'


class DefaultConfig(BaseConfig):

    DEBUG = True

    SQLALCHEMY_ECHO = True
#    dbhost =  os.environ.get('SHARED_DATABASE_URL')
#    dbhost = 'mysql://51828:EFDOtest;;@mysql2.alwaysdata.com/efdigitalorlas_orlas'
#    SQLALCHEMY_DATABASE_URI = dbhost

    # Sqlite
#    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/fbone.db'
    SQLALCHEMY_DATABASE_URI = 'mysql://orlas:salro@localhost/orlas'
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
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'efdigitalorlas.test'
    MAIL_PASSWORD = 'EFDOtest'
    DEFAULT_MAIL_SENDER = '%s@gmail.com' % MAIL_USERNAME


class TestConfig(BaseConfig):
    TESTING = True
    CSRF_ENABLED = False

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
