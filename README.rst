Octodus: A Flask skeleton
=======================

Octodus is `Flask <http://flask.pocoo.org>`_ skeleton, which records how I learn and use Flask.


Features
--------

- Register, login, logout, remember me and reset password.
- Use `twitter/bootstrap <https://github.com/twitter/bootstrap>`_ and `HTML5 Boilerplate <https://github.com/h5bp/html5-boilerplate>`_.
- Handle forms with `WTForms <http://wtforms.simplecodes.com/>`_.
- Handle database with `SQLAlchemy <http://www.sqlalchemy.org>`_.
- `Deploy on Apache + mod_wsgi with fabric <http://flask.pocoo.org/docs/deploying/mod_wsgi/>`_.
- i18n support with `Flask-Babel <http://packages.python.org/Flask-Babel/>`_.
- Unit testing with `Flask-Testing <http://packages.python.org/Flask-Testing/>`_.


Usage
-----

Install packages: ::

    $ python setup.py install

Run local server: ::

    $ python shell.py run

Reset database: ::

    $ python shell.py reset

Compile with babel: ::
    
    $ python setup.py compile_catalog --directory fbone/translations --locale zh -f
