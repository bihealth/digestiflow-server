SODAR Django Site
^^^^^^^^^^^^^^^^^

This project contains a minimal `Django 1.11 <https://docs.djangoproject.com/en/1.11/>`_
site for building `SODAR Core <https://cubi-gitlab.bihealth.org/CUBI_Engineering/CUBI_Data_Mgmt/sodar_core>`_
based projects.


Introduction
============

The site is based on one created by the last Django 1.11 release of
`cookiecutter-django <https://github.com/pydanny/cookiecutter-django/releases/tag/1.11.10>`_.
That project has since moved on to Django 2.x which is not yet supported by
SODAR Core. This template site remains in 1.11, while updating base requirements
and omitting things not relevant to SODAR Core based sites.

Included in this project are the critical OS and Python requirements, pre-set
Django settings, a pre-installed SODAR Core framework and some helper scripts.
It is also readily compatible with Selenium UI testing, coverage checking and
GitLab continuous integration.

The current version of this site is compatible with
`SODAR Core v0.3.0 <https://cubi-gitlab.bihealth.org/CUBI_Engineering/CUBI_Data_Mgmt/sodar_core/tags/v0.3.0>`_.


Installation for Development
============================

For instructions and best practices in Django development, see
`Django 1.11 documentation <https://docs.djangoproject.com/en/1.11/>`_ and
`Two Scoops of Django <https://twoscoopspress.com/products/two-scoops-of-django-1-11>`_.

For SODAR Core concepts and instructions, see
`SODAR Core documentation <https://cubi-gitlab.bihealth.org/CUBI_Engineering/CUBI_Data_Mgmt/sodar_core/tree/v0.3.0/docs>`_.

The examples here use virtualenv and pip, but you may also use e.g. conda for
virtual environments and installing packages.

Install OS and Python Prerequisites
-----------------------------------

Install OS and Python dependencies as follows.

::

    $ sudo utility/install_os_dependencies.sh install
    $ sudo utility/install_chrome.sh
    $ pip install --upgrade pip
    $ utility/install_python_dependencies.sh install

Create Postgres Database
------------------------

Create a Postgres user and database for your project with appropriate names for
your site.

::

    $ sudo adduser --no-create-home sodar_django_site
    $ sudo su - postgres
    $ psql
    $ CREATE DATABASE sodar_django_site;
    $ CREATE USER sodar WITH PASSWORD 'sodar_django_site';
    $ GRANT ALL PRIVILEGES ON DATABASE sodar_django_site TO sodar_django_site;
    $ ALTER USER sodar_django_site CREATEDB;
    $ \q

Set Up Virtual Environment
--------------------------

Set up and activate a virtual environment for running the site. Example below.

::

    $ virtualenv -p python3.6 .venv
    $ source .venv/bin/activate

Install Python Requirements
---------------------------

Install Python requirements for local development.

::

    $ pip install -r requirements/local.txt
    $ pip install -r requirements/test.txt

If you intend to provide LDAP/AD login functionality for your server, also run
the following.

::

    $ pip install -r requirements/ldap.txt

Rename Site
-----------

Rename the ``sodar_django_site`` directory under your project into the name of
your site.

**NOTE:** Make sure to search for mentions to ``sodar_django_site`` within files
and also rename those.

Set Up an Environment Variable File
-----------------------------------

Within the project directory, create an ``.env`` file with environment settings
for the site. You can use the ``env.example`` file as example.

Make sure to add the Postgres database configuration to your .env file as
shown in the example below.

::

    $ export DATABASE_URL='postgres://sodar_django_site:sodar_django_site@127.0.0.1/sodar_django_site'

Set Up Django Database and Superuser
------------------------------------

Run the following command to migrate your Django database and synchronize
SODAR Core plugins.

::

    $ ./manage.py migrate

Next create a superuser for your site.

::

    $ ./manage.py createsuperuser

**NOTE:** If you are running your site in the ``TARGET`` mode, make sure the
``PROJECTROLES_ADMIN_OWNER`` variable in your .env file points to the username
of a local superuser.

Vue App Setup
-------------

Install dependencies

``npm install``

Serve with hot reload at localhost:8080

``npm run dev``

Build for production with minification

``npm run build``

Build for production and view the bundle analyzer report

``npm run build --report``

Run unit tests

``npm run unit``

Run e2e tests

``npm run e2e``

Run all tests

``npm test``

For a detailed explanation on how things work, check out:

* http://vuejs-templates.github.io/webpack/
* http://vuejs.github.io/vue-loader

Run Your Site
-------------

Now you should be able to run your site.

::

    $ ./run.sh

Navigate to `http://0.0.0.0:8000/ <http://0.0.0.0:8000/>`_ and log in to see the
results. The site should be up and running with the default SODAR Core layout.


Developing your Site
====================

Once the installation is successful, you can continue to add your own
SODAR based apps. See
`SODAR Core documentation <https://cubi-gitlab.bihealth.org/CUBI_Engineering/CUBI_Data_Mgmt/sodar_core/tree/v0.3.0/docs>`_.
for further instructions.
