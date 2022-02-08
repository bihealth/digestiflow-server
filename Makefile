.PHONY: default migrate shell dbshell black test celery serve html xml

default:
	@echo "USAGE: make migrate|shell|dbshell|black|test"

celery:
	celery -A config.celery_app worker -l info --concurrency=4 --beat

migrate:
	python manage.py makemigrations
	python manage.py migrate

dbshell:
	python manage.py dbshell

shell:
	python manage.py shell

black:
	black -l 100 . --exclude src

serve:
	python manage.py runserver

test:
	black -l 100 --check --exclude "/(\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist|src)/" .
	flake8 .
	coverage run --rcfile=setup.cfg manage.py test -v2 --settings=config.settings.test
	coverage report

html:
	coverage html

xml:
	coverage xml
