.. image:: https://readthedocs.org/projects/digestiflow-server/badge/?version=master
    :target: https://digestiflow-server.readthedocs.io/en/master/?badge=master
    :alt: Documentation Status

.. image:: https://img.shields.io/travis/bihealth/digestiflow-server.svg
    :target: https://travis-ci.org/bihealth/digestiflow-server

.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :target: https://opensource.org/licenses/MIT

.. image:: https://api.codacy.com/project/badge/Grade/7e9c21b3ba844a1588a7d7fa6e4f82d4
    :target: https://www.codacy.com/app/bihealth/digestiflow-server?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/digestiflow-server&amp;utm_campaign=Badge_Grade

.. image:: https://api.codacy.com/project/badge/Coverage/7e9c21b3ba844a1588a7d7fa6e4f82d4
    :target: https://www.codacy.com/app/bihealth/digestiflow-server?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/digestiflow-server&amp;utm_campaign=Badge_Coverage

.. image:: https://www.herokucdn.com/deploy/button.svg
    :height: 20px
    :alt: Deploy to Heroku
    :target: https://heroku.com/deploy?template=https://github.com/bihealth/digestiflow-server/tree/master

===============
Digestiflow Server
===============

This project contains the code for the Digestiflow Server component of the Digestiflow Suite.
The sibling projects are:

- `Digestiflow CLI <https://github.com/bihealth/digestiflow-cli>`_: command line client
- `Digestiflow Demux <https://github.com/bihealth/digestiflow-demux>`_: (semi)-automated demultiplexing of Illumina flow cells.

-----------------
Digestiflow Suite
-----------------

**Digestiflow Server** is the central component.
It provides a a database system for managing Illumina flow cells and libraries with a web-based UI and a REST API.
Its features include managing sample sheets, quality reports, a minimal "lab notebook" for note-taking and messaging, and sending out notifications on status changes.

**Digestiflow CLI** allows you to extract meta data and adapter index information from sequencer output directories.
Usually, this is run in a regular (e.g., cron) job to monitor the directories where your sequencers store their output to automatically register new flow cells.

**Digestiflow Demux** allows you to demultiplex your flow cell data (semi)-automatically.
Using the sample sheets entered in to Digestiflow Server, performs demultiplexing.
This can also be run in a regular job to demultiplex flow cells as soon as sample sheets are provided in Digestiflow Server and marked as "ready for demultiplexing" there.

------------
Installation
------------

Please refer to the `Installation <https://digestiflow-server.readthedocs.io/en/latest/first_steps_installation.html>`_ section of the `Documentation <https://digestiflow-server.readthedocs.io/en/>`_ on how to install Digestiflow Server.

The recommended way is to `Install with Docker Compose <file:///vol/local/projects/Project_Flowcell/digestiflow-server/docs_manual/_build/html/first_steps_installation.html#install-with-docker-compose>`_.
