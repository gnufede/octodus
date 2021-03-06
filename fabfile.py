# -*- coding: utf-8 -*-

from fabric.api import *

# the user to use for the remote commands
env.user = 'user_of_deploy_machine'
# the servers where the commands are executed
env.hosts = ['ip_of_deploy_machine']

def pack():
    # create a new source distribution as tarball
    local('python setup.py sdist --formats=gztar', capture=False)

def deploy():
    pack()
    # figure out the release name and version
    dist = local('python setup.py --fullname', capture=True).strip()
    # upload the source tarball to the temporary folder on the server
    put('dist/%s.tar.gz' % dist, '/tmp/octodus.tar.gz')
    # create a place where we can unzip the tarball, then enter
    # that directory and unzip it
    run('mkdir /tmp/octodus')
    with cd('/tmp/octodus'):
        run('tar xzf /tmp/octodus.tar.gz')
    with cd('/tmp/octodus/%s' % dist):
        # now setup the package with our virtual environment's
        # python interpreter
        run('/var/www/octodus/env/bin/python setup.py install')
    # now that all is set up, delete the folder again
    run('rm -rf /tmp/octodus /tmp/octodus.tar.gz')
    # and finally touch the .wsgi file so that mod_wsgi triggers
    # a reload of the application
    run('touch /var/www/octodus.wsgi')
