.. image:: https://img.shields.io/travis/bihealth/digestiflow-web.svg
    :target: https://travis-ci.org/bihealth/digestiflow-web

.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :target: https://opensource.org/licenses/MIT

.. image:: https://api.codacy.com/project/badge/Grade/7e9c21b3ba844a1588a7d7fa6e4f82d4
    :target: https://www.codacy.com/app/bihealth/digestiflow-web?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/digestiflow-web&amp;utm_campaign=Badge_Grade

.. image:: https://api.codacy.com/project/badge/Coverage/7e9c21b3ba844a1588a7d7fa6e4f82d4
    :target: https://www.codacy.com/app/bihealth/digestiflow-web?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/digestiflow-web&amp;utm_campaign=Badge_Coverage

.. image:: https://www.herokucdn.com/deploy/button.svg
    :height: 20px
    :alt: Deploy to Heroku
    :target: https://heroku.com/deploy?template=https://github.com/bihealth/digestiflow-web/tree/master

===============
Digestiflow Web
===============

This project contains the code for the Digestiflow Web component of the Digestiflow Suite.
The sibling projects are:

- `Digestiflow CLI <https://github.com/bihealth/digestiflow-cli>`_: command line client
- `Digestiflow Demux <https://github.com/bihealth/digestiflow-demux>`_: (semi)-automated demultiplexing of Illumina flow cells.

-----------------
Digestiflow Suite
-----------------

**Digestiflow Web** is the central component.
It provides a a database system for managing Illumina flow cells and libraries with a web-based UI and a REST API.
Its features include managing sample sheets, quality reports, a minimal "lab notebook" for note-taking and messaging, and sending out notifications on status changes.

**Digestiflow CLI** allows you to extract meta data and adapter index information from sequencer output directories.
Usually, this is run in a regular (e.g., cron) job to monitor the directories where your sequencers store their output to automatically register new flow cells.

**Digestiflow Demux** allows you to demultiplex your flow cell data (semi)-automatically.
Using the sample sheets entered in to Digestiflow Web, performs demultiplexing.
This can also be run in a regular job to demultiplex flow cells as soon as sample sheets are provided in Digestiflow Web and marked as "ready for demultiplexing" there.

------------
Installation
------------

Deploy to Heroku
================

The easiest way to try out Digestiflow Web is to click `Deploy to Heroku <https://heroku.com/deploy?template=https://github.com/bihealth/digestiflow-web/tree/master>`_ (or the button above) and follow the step-by-step process.

1. Create an account and sign in if necessary.
2. Set the application name, e.g., to ``my-digestiflow-demo``.
3. Click **Deploy app** and... wait a bit.
    - It seems that, sadly, you will have to enter credit card for account verification.
      Note that you can try out Digestiflow Web with free/hobby plan only.
      Also, this is a bit unintuitive, deployment will fail.
      You have to enter your credit card information and then continue...
4. After deployment has succeeded, go to ``Manage App``, then ``Settings`` in the Heroku Dashboard.
   There, click ``Reveal Config Vars`` and copy the value after ``DIGESTIFLOW_INITIAL_ROOT_PASSWORD`` into your clipboard.
5. Go to https://my-digestiflow-demo.herokuapp.com/login/ and login as `root` with the root password copied above.
6. Finally click the little user icon on the top left and then `Admin`.
   Here you can change the root user's password, create new users etc.

From here, you can read the built-in manual at https://my-digestiflow-demo.herokuapp.com/manual/ (or clicking "Manual" in the right of the top navigation bar).

Self-Hosting Digestiflow Web
============================

Digestiflow CLI and Digestiflow Demux can be installed using Conda and the Bioconda channel.
See the individual projects' documentation.

Digestiflow Web ...

TODO: write me!
