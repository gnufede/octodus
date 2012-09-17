#!/bin/sh
rsync -az /home/efdigital/lib/python2.6/fbone-0.1-py2.6.egg/fbone/static/offers/ ~/offers
cd ~/webapps/fbone/htdocs;
git pull;
~/webapps/fbone/apache/bin/stop
python2.6 setup.py install
~/webapps/fbone/apache/bin/start
rsync -az ~/offers/ /home/efdigital/lib/python2.6/fbone-0.1-py2.6.egg/fbone/static/offers

