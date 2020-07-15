#!/bin/sh

echo $DATABASE

if [ "$DATABASE" = "postgres" ]; then
    echo "\nWaiting for postgres..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
      sleep 0.1
    done

    echo "\nPostgreSQL started"
fi

# Load DJANGO_SUPERUSER secrets into env vars, so createsuperuser command finds them
if [ -e /var/run/secrets/django_superuser_email ]; then
    echo "\nDocker secrets detected, loading super user secrets into env vars."

    export DJANGO_SUPERUSER_EMAIL=$(cat /var/run/secrets/django_superuser_email)
    export DJANGO_SUPERUSER_PASSWORD=$(cat /var/run/secrets/django_superuser_password)
fi

# Make migrations and migrate the database.
echo "\nMaking migrations and migrating the database."
python manage.py makemigrations portfolio --noinput 
python manage.py migrate --noinput 


# Try setting env var admin password, redirect error output to dev/null
python manage.py shell --command="import os
from django.contrib.auth.models import User
u = User.objects.get(username=os.getenv('DJANGO_SUPERUSER_USERNAME'))
u.set_password(os.getenv('DJANGO_SUPERUSER_PASSWORD'))
u.save()
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "\nSet django superuser password"
else
    #if admin does not exist createsuperuser
    echo "\nCreating django superuser"
    python manage.py createsuperuser --no-input
fi


echo "\nImporting core data"
python manage.py shell --command="from django.contrib.contenttypes.models import ContentType; ContentType.objects.all().delete()"
python manage.py loaddata portfolio.json

echo "\nCollecting static files"
python manage.py collectstatic --noinput

exec "$@"