.PHONY: default migrate shell dbshell black test celery serve

default:
	@echo "USAGE: make migrate|shell|dbshell|black|test"

celery:
	celery worker -A config.celery_app -l info --concurrency=4 --beat

migrate:
	python manage.py makemigrations
	python manage.py migrate

dbshell:
	python manage.py dbshell

shell:
	python manage.py shell

black:
	black -l 100 .

serve:
	python manage.py runserver

test:
	coverage run --rcfile=setup.cfg manage.py test -v2 --settings=config.settings.test
	coverage report
