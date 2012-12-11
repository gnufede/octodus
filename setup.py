# -*- coding: utf-8 -*-

from setuptools import setup
#from babel.messages import frontend as babel


setup(
    name='octodus',
    version='0.1',
    description='Flask Skeleton Project',
    author='Fede Mon',
    author_email='gnufede@gmail.com',
    packages=['octodus'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask ==0.9',
        'Flask-SQLAlchemy ==0.16',
        'Flask-WTF ==0.8',
        'Flask-Script ==0.3.3',
        'Flask-Babel ==0.8',
        'Flask-Testing ==0.4',
        'Flask-Uploads ==0.1.3',
        'Flask-Mail ==0.6.1',
        'Flask-Cache ==0.4.0',
        'Flask-Login ==0.1.3',
        'Flask-gzip ==0.1',
        'MySQL-python ==1.2.3',
        'nose ==1.1.2',
        'python-dateutil ==2.1',
        'chardet ==1.1'
    ]
)
