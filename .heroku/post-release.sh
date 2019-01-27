#!/bin/bash

>&2 echo "BEGIN: Post-release script -----------------------------------------"

>&2 echo "BEGIN: Database migrations..."
python manage.py migrate --noinput
>&2 echo "DONE: Database migrations"

>&2 echo "END: Post-release script -------------------------------------------"
