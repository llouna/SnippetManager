# A module to be loaded by uwsgi to serve HTTP requests
wsgi: snippet.wsgi:application
release: ./manage.py migrate && ./manage.py collectstatic --noinput && ./manage.py loaddata langage
# A background worker
# worker: python long_running_script.py
# Another worker with a different name
# fetcher: python fetcher.py
# Simple cron expression: minute [0-59], hour [0-23], day [0-31], month [1-12], weekday [1-7] (starting Monday, no ranges allowed on any field)
# cron: 0 0 * * * python midnight_cleanup.py
# release: python initial_cleanup.py