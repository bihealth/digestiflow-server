.. _first_steps_installation:

============
Installation
============

This section describes the installation of Digestiflow, in particular Digestiflow Server.
Digestiflow Server provides the database for the flow cells and barcodes as well as the REST API.
As a server component, it is the most complex component of Digestiflow Suite to setup.
You will be able to install the client components Digestiflow CLI and Digestiflow Demux as standalone (Bio-)conda packages which will be considerably easier.

Overall, Digestiflow Server is a `Twelve-Factor App <https://12factor.net/>`_ which means that it is fairly easy to deploy (as modern web applications go) but you will have to fulfill a few prerequisites.
Further, we will outline the specific installation and configuration steps below.
In the Digestiflow Server repository, you will also find a directory ``ansible`` which contains some Ansible playbooks that you can base your own Ansible playbooks for the installation on.
It should be easy convert this into your existing server management infrastructure (Ansible, Puppet, Salt, ...)

-------------
Prerequisites
-------------

You will need to have the following prerequisites fulfilled.

Linux/Unixoid Operating System
    The following instructions have been tested on Linux.
    Your mileage might vary for Mac or Windows Linux Subsystem etc.
Linux/Unix Experience
    Intermediate knowledge about managing a Linux/Unix system will be required.
Python 3, >=3.5
    Digestiflow Server is a Django-based web server and requires Python 3.
Python Virtualenv
    You should be able to run the ``virtualenv`` command.
    Consult your operating system's or Python distribution's manual on how to do this.
PostgreSQL, >=9.5
    A modern PostgreSQL installation is required for storing the data.
Redis
    A key/value store required for caching and task queues.

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

If you have not done so yet, follow the `Docker CE installation instructions <https://docs.docker.com/install/>_` for installing Docker itself.

Install Docker (Compose)
========================

E.g., on CentOS

.. code-block:: shell

    $ sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine
    $ sudo yum install -y yum-utils device-mapper-persistent-data lvm2
    $ sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    $ sudo yum install docker-ce docker-ce-cli containerd.io
    $ sudo systemctl enable docker
    $ sudo systemctl start docker
    $ sudo curl -L "https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    $ sudo chmod +x /usr/local/bin/docker-compose

or on Ubuntu:

.. code-block:: shell

    $ sudo apt-get remove docker docker-engine docker.io containerd runc
    $ sudo apt-get update
    $ sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
    $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    $ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    $ sudo apt-get update
    $ sudo apt-get install docker-ce docker-ce-cli containerd.io
    $ sudo curl -L "https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    $ sudo chmod +x /usr/local/bin/docker-compose

Digestiflow Server with Docker Compose
======================================

First, checkout the source code

.. code-block:: shell

    $ git clone https://github.com/bihealth/digestiflow-server.git

Next, simply call `sudo docker-compose up` in the `docker` sub folder of your setup

.. code-block:: shell

    $ cd digestiflow-server/docker
    $ sudo docker-compose up
    Creating network "docker_db_network" with driver "bridge"
    Creating network "docker_nginx_network" with driver "bridge"
    Creating volume "docker_db_volume" with default driver
    Pulling db (postgres:9.6)...
    9.6: Pulling from library/postgres
    27833a3ba0a5: Pull complete
    [...]
    web_1    | [2019-04-10 21:04:58 +0000] [1] [INFO] Starting gunicorn 19.9.0
    web_1    | [2019-04-10 21:04:58 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
    web_1    | [2019-04-10 21:04:58 +0000] [1] [INFO] Using worker: sync
    web_1    | [2019-04-10 21:04:58 +0000] [79] [INFO] Booting worker with pid: 79

You can now log into Digestiflow Server through the following URL (ignore the security warning for the self-signed SSL certificate):

- https://localhost:8443/

You can login with user name `root` and password `root`.

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
