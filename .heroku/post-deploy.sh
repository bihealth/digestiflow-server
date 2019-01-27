#!/bin/bash

>&2 echo "BEGIN: Post-deploy script ------------------------------------------"

>&2 echo "BEGIN: Database migrations..."
python manage.py migrate --noinput
>&2 echo "DONE: Database migrations"

>&2 echo "BEGIN: Creating user 'root'..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('root', 'admin@example.com', '$DIGESTIFLOW_INITIAL_ROOT_PASSWORD')" \
| python manage.py shell
>&2 echo "DONE: Creating user 'root'"

>&2 echo "================================================"
>&2 echo "Auto-created superuser"
>&2 echo ""
>&2 echo "LOGIN:    'root'"
>&2 echo "PASSWORD: '$DIGESTIFLOW_INITIAL_ROOT_PASSWORD'"
>&2 echo ""
>&2 echo "================================================"

>&2 echo "END: Post-deploy script --------------------------------------------"
