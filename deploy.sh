#!/bin/sh
rsync -az /home/efdigital/lib/python2.6/octodus-0.1-py2.6.egg/octodus/static/offers/ ~/offers
cd ~/webapps/octodus/htdocs;
git pull;
~/webapps/octodus/apache2/bin/stop
python2.6 setup.py install
~/webapps/octodus/apache2/bin/start
rsync -az ~/offers/ /home/efdigital/lib/python2.6/octodus-0.1-py2.6.egg/octodus/static/offers

