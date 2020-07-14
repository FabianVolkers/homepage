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

echo "\nCreating django superuser"
python manage.py createsuperuser --no-input

echo "\nImporting core data"
python manage.py shell --command="from django.contrib.contenttypes.models import ContentType; ContentType.objects.all().delete()"
python manage.py loaddata portfolio.json

echo "\nCollecting static files"
python manage.py collectstatic --noinput

exec "$@"