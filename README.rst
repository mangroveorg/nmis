NMIS - Nigerian HEalth Indicators - A Mangrove Client
=====================================================

NMIS displays key health indicators for the Nigerian
government.

Copyright 2011 Columbia Univeristy / The Earth Institute


Setup on Ubuntu 10.10:
======================
Install POSTGRES if you are using it.
::
    sudo apt-get install postgresql-8.4 postgresql-client-8.4 python-psycopg2

Install prerequisites
::
    sudo apt-get install git-core build-essental python2.6-dev python-setuptools
    sudo easy_install pip

Install the NMIS Code base
::
    git clone git://github.com/mangroveorg/mangrove.git
    cd mangrove/src/nmis
    sudo pip install -r requirements.txt
    python manage.py syncdb
    python managae.py runserver

Point NMIS to a Mangrove Server
::
    #edit settings.py
    .
    .
    
THESE INSTRUCTIONS ARE UNDER DEVELOPMENT AND INCOMPLETE AT THE MOMENT