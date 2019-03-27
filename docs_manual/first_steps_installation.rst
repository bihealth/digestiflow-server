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
However, this is just a "formulization" of what you find below and it should be easy convert this into your existing server management infrastructure (Ansible, Puppet, Salt, ...)

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

In the following, we will describe how to:

1. Setup a PostgreSQL user for the web app.
2. Install the web app and setup a virtualenv environment for it.
3. Configure the web app.
4. Initialize the database and create a super user account.
5. Follow a short tutorial on how tutorial
    - create example flow cell base call data,
    - register sequencing machines with Digestiflow,
    - register adapter sequence sets,
    - import the example flow cell into Digestiflow using ``digestiflow-cli``,
    - fill out the sample sheet for this flow cell, and
    - run demultiplexing using ``digestiflow-demux`` using the meta data in Digestiflow Server previously added by ``digestiflow-cli``.

Afterwards, you should explore the rest of the documentation to see the full feature set of Digestiflow.

----------------
PostgreSQL Setup
----------------

If you have not done so already, install the PostgreSQL server.
A version above 9.5 will be required for sufficient support for JSON.
Consult your operating system's manual on how to do this.
There are plenty resources on the internet how to do this, e.g., `How to Install PostgreSQL Relational Datbases on CentOS 7 <https://www.linode.com/docs/databases/postgresql/how-to-install-postgresql-relational-databases-on-centos-7/>`_.
If you are lucky enough, a version of 9.6 or above will be directly available from your Unix distribution.

Once you have installed PostgreSQL, create a database ``digestiflow_server`` owned by a user ``digestiflow_server`` (you can pick any other names but this is what the rest of the tutorial assumes.

After this step, you should be able to connect to the ``digestiflow_server`` database with your ``digestiflow_server`` user.
That user should be able to create database entries such as tables in this database.

---------------
Install Web App
---------------

Installation of the web app is very simple, you just clone it source code via git.
The following will get the latest stable version from branch ``master``:

::

    ~ # git clone https://github.com/bihealth/digestiflow-server.git

Next, create a virtual environment with the requirements for running it in production mode.

::

    ~ # cd digestiflow-server
    digestiflow-server # virtualenv -p python3 .venv
    digestiflow-server # source .venv/bin/activate
    (.venv) digestiflow-server # pip install -r requirements/production.txt
    [...]

Once this is complete, you are ready to configure the web app.

-----------------
Configure Web App
-----------------

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
