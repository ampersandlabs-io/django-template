web: bin/start-pgbouncer-stunnel gunicorn --pythonpath="$PWD/{{ project_name }}" wsgi --log-file - --preload

worker: python {{ project_name }}/manage.py rqworker default
