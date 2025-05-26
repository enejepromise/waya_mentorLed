web: gunicorn waya_backend.wsgi:application
worker: celery -A waya_backend worker --loglevel=info
beat: celery -A waya_backend beat --loglevel=info
