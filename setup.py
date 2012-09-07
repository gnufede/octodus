# -*- coding: utf-8 -*-

from setuptools import setup
#from babel.messages import frontend as babel


setup(
    name='fbone',
    version='0.1',
    description='Flask Skeleton Project',
    author='Wilson Xu',
    author_email='imwilsonxu@gmail.com',
    packages=['fbone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'Flask-Script',
        'Flask-Babel',
        'Flask-Testing',
        'Flask-Uploads',
        'Flask-Mail',
        'Flask-Cache',
        'Flask-Login',
        'MySQL-python',
        'nose',
        'python-dateutil',
    ]
)
