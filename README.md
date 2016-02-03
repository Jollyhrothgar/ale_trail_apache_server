# This Flask webapp is designed to be used with an Apache Webserver Host.

## Step 1
Follow instructions here: https://www.digitalocean.com/community/tutorials/how-to-install-linux-apache-mysql-php-lamp-stack-on-ubuntu

to install and set up the apache webserver.

## Step 2
Follow instructions here to generate a flask-web-app (start to finish template webapp).

https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps

Note that the final directory structure may vary.

For me, the directory structure which eventually worked was:

```
/var/www/FlaskApp
/var/www/FlaskApp/FlaskApp
/var/www/FlaskApp/FlaskApp/__init__.py
/var/www/FlaskApp/FlaskApp/static
/var/www/FlaskApp/FlaskApp/query_results.py (a function used in __init.py__, which has all the @routes and views)
/var/www/FlaskApp/FlaskApp/templates
/var/www/FlaskApp/FlaskApp/venv (python virtual environment)
/var/www/FlaskApp/flaskapp.wsgi
```
## Step 3:
profit

I fooled around with the webapp directory structure while simultaneously running
'tail -f' in a separate terminal over the apache server log, which for me was
located at /var/log/apache2/error.log. This was a great way to check what works,
what doesn't. Additionaly, its fun to run 'tail -f' on the other apache log
files so you can watch people use your site in real time.

Now adding haversine curves to get user to local breweries.
