web: gunicorn cotizapp.wsgi --log-file -
worker: celery -A cotizapp worker -l info
beat: celery -A cotizapp beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
