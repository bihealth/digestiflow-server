.PHONY: default migrate shell dbshell black test celery

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
	python manage.py black

test:
	coverage run manage.py test -v2 --settings=config.settings.test
	coverage report
