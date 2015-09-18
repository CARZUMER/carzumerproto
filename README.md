# carzumerproto
# /opt/www/carzumerproto

1. Make sure that basic python tools are installed

    sudo apt-get --yes install python-setuptools
    sudo easy_install pip
    sudo pip install virtualenv
    
2. Create and switch to a virtual env inside the "carzumerproto" folder

    cd /opt/www/carzumerproto
    
    virtualenv env
    
    source env/bin/activate

2. Install gunicorn:

    pip install gunicorn

3. Install web.py

    pip install web.py

4. Install setptoctitle

    pip install setproctitle

5. Install iPython if you like to make debugging easier
    pip intall ipython




Other configuration:

Install supervisor and configure it to work with gunicorn

    sudo apt-get install supervisor 
    
    sudo chmod 755  gunicorn_start 
    
    mkdir /opt/www/carzumerproto/run/
    sudo chown www-data /opt/www/carzumerproto/run
    
    mkdir -p /opt/www/carzumerproto/logs/
    touch /opt/www/carzumerproto/logs/gunicorn_supervisor.log 

    sudo chmod 757 /opt/www/carzumerproto -R 
    
Setup a symbolic links to the /etc/supervisor/conf.d and to the /etc/nginx/sites-enabled/ 

    sudo ln -s  /opt/www/carzumerproto/carzumerproto_supervisor.conf /etc/supervisor/conf.d/carzumerproto.conf
    sudo ln -s /opt/www/carzumerproto/nginx.conf /etc/nginx/sites-enabled/carzumerproto.conf

To activate new app with supervisor:

    sudo supervisorctl reread
    sudo supervisorctl update


To check the status of the application:

    sudo supervisorctl status carzumerproto

To stop the application
    sudo supervisorctl stop carzumerproto

To start the application
    sudo supervisorctl start carzumerproto
    
To restart the application
    sudo supervisorctl restart carzumerproto
    
To restart nginx:

    sudo service nginx restart

To check the logs:

 tail -100 /opt/www/carzumerproto/logs/gunicorn_supervisor.log
 sudo tail -100 /var/log/supervisor/supervisord.log 
 
 sudo  tail /var/log/nginx/carzumerproto-access.log 
 sudo  tail /var/log/nginx/error.log 
 
 


