.. image:: https://img.shields.io/travis/bihealth/digestiflow-web.svg
    :target: https://travis-ci.org/bihealth/sodar_core

.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :target: https://opensource.org/licenses/MIT

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

Digestiflow CLI and Digestiflow Demux can be installed using Conda and the Bioconda channel.
See the individual projects' documentation.

Digestiflow Web ...

TODO: write me!
