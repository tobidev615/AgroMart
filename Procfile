web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn farmfresh.wsgi:application --bind 0.0.0.0:$PORT --workers 3
