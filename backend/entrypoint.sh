#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
username='${DJANGO_SUPERUSER_USERNAME}';
email='${DJANGO_SUPERUSER_EMAIL}';
password='${DJANGO_SUPERUSER_PASSWORD}';
user, created = User.objects.get_or_create(username=username, defaults={'email': email});
user.email = email;
user.is_staff = True;
user.is_superuser = True;
if hasattr(user, 'role'):
    user.role = 'admin';
user.set_password(password);
user.save();
"
fi

exec gunicorn issue_tracker.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
