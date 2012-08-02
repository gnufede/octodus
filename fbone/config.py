# -*- coding: utf-8 -*-

APP_NAME = 'fbone'

class BaseConfig(object):

    DEBUG = True
    TESTING = False

    # os.urandom(24)
    SECRET_KEY = 'secret key'


class DefaultConfig(BaseConfig):

    DEBUG = True

    SQLALCHEMY_ECHO = True
    # Sqlite
#    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/fbone.db'
    SQLALCHEMY_DATABASE_URI = 'mysql://orlas:salro@localhost/orlas'
    # Mysql: 'mysql://dbusername:dbpassword@dbhost/dbname'

    # To create log folder.
    # $ sudo mkdir -p /var/log/fbone
    # $ sudo chown $USER /var/log/fbone
    DEBUG_LOG = '/tmp/fbone-debug.log'

    ACCEPT_LANGUAGES = ['en']
    BABEL_DEFAULT_LOCALE = 'es'

    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 60

    # Email (Flask-email)
    # https://bitbucket.org/danjac/flask-mail/issue/3/problem-with-gmails-smtp-server
    MAIL_DEBUG = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'gnu.fede'
    MAIL_PASSWORD = '#faif#99GGL'
    DEFAULT_MAIL_SENDER = '%s@gmail.com' % MAIL_USERNAME


class TestConfig(BaseConfig):
    TESTING = False
    CSRF_ENABLED = False

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
