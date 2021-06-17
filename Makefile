# Make commands for development
# 
# `make build` installs required modules and generates required migrations.
# `make run` runs the Django server, listening on port 8000.
# `make celery` runs a Celery worker.  Needs to be restarted manually when code changes.

PIP=pip
PYTHON=python
CELERY=celery

build: requirements.flag
	$(PYTHON) ./manage.py makemigrations

requirements.txt: requirements.in
	$(PIP) install -r requirements.in
	echo "# GENERATED FROM requirements.in.  DO NOT EDIT DIRECTLY." > requirements.txt
	$(PIP) freeze >> requirements.txt

requirements.flag: requirements.txt
	$(PIP) install -r requirements.txt
	touch requirements.flag

run: build
	$(PYTHON) ./manage.py migrate
	$(PYTHON) ./manage.py runserver

celery: build
	$(CELERY) multi start w1 -A main --beat --pidfile=logs/celery-%n.pid --logfile=logs/celery-%n%I.log --loglevel=debug

nocelery: build
	$(CELERY) multi stopwait w1 -A main --beat --pidfile=logs/celery-%n.pid --logfile=logs/celery-%n%I.log --loglevel=debug

clean:
	rm -rf dist .cache build
