.. _first_steps_installation:

============
Installation
============

This section describes the installation of Digestiflow, in particular Digestiflow Server.
Digestiflow Server provides the database for the flow cells and barcodes as well as the REST API.
As a server component, it is the most complex component of Digestiflow Suite to setup.
You will be able to install the client components Digestiflow CLI and Digestiflow Demux as standalone (Bio-)conda packages which will be considerably easier.

Overall, Digestiflow Server is a `Twelve-Factor App <https://12factor.net/>`_ which means that it is fairly easy to deploy (as modern web applications go) but you will have to fulfill a few prerequisites.
We strongly recommend the setup using Docker Compose and the instructions below refer to this.
You can also find a Quickstart tutorial in the `digestiflow-docker-compose <https://github.com/bihealth/digestiflow-docker-compose/>`_ Github repository.

-------------
Prerequisites
-------------

You will need to have the following prerequisites fulfilled.

Linux with Docker Compose
    The following instructions have been tested on Linux.
    Your mileage might vary for Mac or Windows Linux Subsystem etc.

--------
Overview
--------

In the following, we will describe how to either

a. install via `Docker Compose <https://docs.docker.com/compose/>`_ **for testing Digestiflow (recommended)**, or
b. perform a manual installation on a Linux server

    1. setup a PostgreSQL user for the web app,
    2. install the web app and setup a virtualenv environment for it,
    3. configure the web app, and
    4. initialize the database and create a super user account, or

c. deploy to the Heroku platform (for free but a credit card is required for registration.

Afterwards, you should follow through the tutorial and then explore the rest of the documentation to see the full feature set of Digestiflow.

---------------------------
Install with Docker Compose
---------------------------

If you have not done so yet, follow the `Get Docker <https://docs.docker.com/install/>`_ for installing Docker Engine itself and `Install Docker Compose <https://docs.docker.com/compose/install/>`_

Next, you will use Docker Compose to startup a server.
First, checkout the digestiflow-docker-compose repository.

.. code-block:: shell

    $ git clone https://github.com/bihealth/digestiflow-docker-compose.git

Next, initialize some directories, copy the example configuration file to ``.env`` and optionally adjust the settings.

.. code-block:: shell

    $ bash init.sh
    $ cp env.example .env
    $ $EDIT .env

Finally, simply call `sudo docker-compose up` folder of your setup

.. code-block:: shell

    $ cd digestiflow-docker-compose
    $ sudo docker-compose up
    Creating digestiflow-docker-compose_redis_1    ... done
    Creating digestiflow-docker-compose_traefik_1  ... done
    Creating digestiflow-docker-compose_postgres_1 ... done
    Creating digestiflow-docker-compose_digestiflow-web_1 ... done
    Creating digestiflow-docker-compose_digestiflow-celeryd-default_1 ... done
    Creating digestiflow-docker-compose_digestiflow-celerybeat_1      ... done
    Attaching to digestiflow-docker-compose_redis_1, digestiflow-docker-compose_traefik_1, digestiflow-docker-compose_postgres_1, digestiflow-docker-compose_digestiflow-web_1, digestiflow-docker-compose_digestiflow-celeryd-default_1, digestiflow-docker-compose_digestiflow-celerybeat_1
    digestiflow-web_1              | [2021-07-20 09:16:28 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
    digestiflow-web_1              | [2021-07-20 09:16:28 +0000] [1] [INFO] Using worker: sync
    digestiflow-web_1              | [2021-07-20 09:16:28 +0000] [21] [INFO] Booting worker with pid: 21

If everything went well, either start the server in the background (``docker-compose up -d``) or open a new terminal to create a ``root`` user:

.. code-block:: shell

    $ docker-compose exec digestiflow-web python /usr/src/app/manage.py createsuperuser \
    --username root
    Email address:
    Password:
    Password (again):
    Superuser created successfully.

You can now log into Digestiflow Server through the following URL (ignore the security warning for the self-signed SSL certificate):

- https://<your-host-maybe-localhost>/

You can login with user name `root` and the password that you used above.

-------------------
Manual Installation
-------------------

The following assumes a CentOS 7.4 system but you should be able to adjust it to any modern Linux distribution.

First, install the required packages.

.. code-block:: shell

    ### install EPEL repository
    $ yum install -y epel-release
    ### install IUS repository and packages
    $ yum install -y https://centos7.iuscommunity.org/ius-release.rpm
    $ yum install -y python36u python36u-pip python36u-devel python36-upsycopg2
    ### install Postgres repository and packages
    $ yum install -y https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-redhat96-9.6-3.noarch.rpm
    $ yum install -y postgresql96-server postgresql96-devel postgresql96-contrib

PostgreSQL Setup
================

Creating a user and database through the ``createuser`` and ``createdb`` commands is easiest.
You have to do this as the ``postgres`` user.
We're using ``digestiflow_server`` both for the user name and password.
You should pick a better password!

.. code-block:: shell

    $ sudo -u postgres createuser -E digestiflow_server
    Enter password for new role: digestiflow_server
    Enter it again: digestiflow_server
    $ createdb -l UTF-8 -O digestiflow_server

You have now setup a database ``digestiflow_server`` owned by the user ``digestiflow_server``.

.. info:

    Note that you might have to configure PostgreSQL to allow password hash based authentication.
    For this, add the following line to the ``pbg_hba.conf`` file (see `PostgreSQL documentation <https://www.postgresql.org/docs/current/auth-pg-hba-conf.html>`_).

    .. code-block::

        host  postgres  all  127.0.0.1/32  md5

Install Web App
===============

Installation of the web app is very simple, you just clone it source code via git.
The following will get the latest stable version from branch ``master``:

::

    # git clone https://github.com/bihealth/digestiflow-server.git

Next, create a virtual environment with the dependencies for running it in production mode.

::

    # virtualenv -p python3 digestiflow-server-venv
    # source digestiflow-server-venv/bin/activate
    (digestiflow-server-venv) # cd digestiflow-server-venv
    (digestiflow-server-venv) # pip install -r requirements/production.txt
    [...]

Once this is complete, you are ready to configure the web app.

Configure Web App
=================

All of Digestiflow Server can be configured as environment variables as is common for a `Twelve-Factor App <https://12factor.net/>`_.
This has the advantage that you do not have to touch Digestiflow Server's source code and all configuration can be done outside it (e.g., in a ``systemd`` environment file as shown in the Ansible files shipping with the source code).

The following shows a set of the available environment variables, the required ones are marked with ``#**``.
Put the following into a file ``.env`` in your ``digestiflow-server`` checkout and adjust it to your liking and requirements.

::

    # Disable debugging (is default)
    DJANGO_DEBUG=0

    #** PostgreSQL configure user:password@host/database_name for PostgreSQL connection
    DATABASE_URL="postgres://digestiflow_server:digestiflow_server@127.0.0.1/digestiflow_server"

    #** Use production settings
    DJANGO_SETTINGS_MODULE=config.settings.production
    #** Configure secret key for session etc.
    DJANGO_SECRET_KEY=CHANGE_ME!!!

    # Configuration for sending out emails
    EMAIL_SENDER=CHANGE_ME@example.com
    EMAIL_URL=smtp://CHANGE_ME.example.com
    EMAIL_SUBJECT_PREFIX="[Your SODAR Django Site]"

    # You can enable LDAP authentication for up to two different sites.  See
    # django-auth-ldap documentation for more details.
    ENABLE_LDAP=0
    AUTH_LDAP_SERVER_URI=
    AUTH_LDAP_BIND_PASSWORD=
    AUTH_LDAP_BIND_DN=
    AUTH_LDAP_USER_SEARCH_BASE=
    AUTH_LDAP_USERNAME_DOMAIN=
    AUTH_LDAP_DOMAIN_PRINTABLE=

    ENABLE_LDAP_SECONDARY=0
    AUTH_LDAP2_SERVER_URI=
    AUTH_LDAP2_BIND_PASSWORD=
    AUTH_LDAP2_BIND_DN=
    AUTH_LDAP2_USER_SEARCH_BASE=
    AUTH_LDAP2_USERNAME_DOMAIN=
    AUTH_LDAP2_DOMAIN_PRINTABLE=

    # Configuration for SODAR-core projectroles app
    PROJECTROLES_SEND_EMAIL=1
    PROJECTROLES_SITE_MODE=TARGET
    PROJECTROLES_TARGET_CREATE=1
    #** Name of the super user, adjust if you change the superuser name below.
    PROJECTROLES_ADMIN_OWNER=admin

    #** Configure URL to Redis, this is for a default Redis installation
    CELERY_BROKER_URL=redis://localhost:6379/0

Once complete, you can use the following to create a admin/super user.
Make sure that you have your virtualenv activated.

::

    # python manage.py createsuperuser
    [follow on-screen instruction]

Once you have completed this step, you can use the following command for starting up the server.
Do this and log in as the super use you just created.

::

    # python manage.py migrate
    # python manage.py collectstatic
    # python manage.py runserver
    [now direct your browser to the displayed URL and login]
