.. _flowcells_overview:

==================
Flow Cell Overview
==================

Flow cells are easily the most complex object in Digestiflow as they relate to the sequencer object that the flow cell was sequenced with, contain libraries and each library can relate to one or two barcodes used for them.
Further, the sequencing, demultiplexing, and delivery state (cf. :ref:`first_steps_overview`) is modelled as flow cell attributes.

In the data model of Digestiflow, a "flow cell" actually means a "flow cell run", that is the information that the flow cell with a given ID was processed as the i-th flowcell in a given sequencing machine.
It *is* possible to have a flow cell appear in two runs (and thus have two runs with the same flow cel ID), e.g., if the operator detects an error after starting the sequencer and immediately cancels the sequencing.
Given the correct timing, the flow cell will remain unused and can be started again (with an incremented run number, though).
As this case will be very rare (and the cancelled run does not generate any sequencing data), we will use the simplification of referring to "flow cell run" as "flow cell".

---------------
Run Directories
---------------

The sequencing devices store flow cell **run directories** with the following naming scheme.
The different parts of the directories are separated by undescores.

::

                          run number on     flow cell
    date/month/year         sequencer       vendor ID
        .----.                .----.      .----------.
        |    |                |    |      |          |
        YYMMDD_MACHINE-VENDOR_RUN-NO_SLOT_FLOW-CELL-ID_LABEL
               |            |        |  |              |   |
               '------------'        '--'              '---'
             machine vendor ID    the slot can     user-defined label
                                    be A or B         for flow cell

There are some caveats:

- The trailing underscore is missing for NextSeq (where the slot is always ``A``), such that there is a field less and the flow cell ID field always starts with an ``A``.
- The label might be missing (also no underscore), be empty (trailing undescore) and might contain whitespace.

---------
RTA Files
---------

The Illumina machines run a software called "RTA" (Run-Time-Analysis) that is responsible for operating the machine and everything from base calling, writing out statistics, storing thumbnail images, and displaying online quality control measures.
The RTA also creates files describing the machine configuration and run parameters as well as the current sequencing state.

Digestiflow extracts its required metadata information from the sequencing output directory and the files created by RTA.
This implies that only properly formatted run directories can be imported (if they deviate from the description above, Digestiflow CLI and Demux will not work properly).

-----------------
Flow Cell Records
-----------------

Each flow cell has various properties described in :ref:`flowcells_details` and refers to the Sequencer database object it was run on.
This implies that you have to register all sequencers that you would like to in a given site.
Note that the sequencer vendor ID has to be unique within each site and you have to register each sequencer individually in the site that you want to use it in.

Each flow cell contains a list of libraries.
Each of these libraries has a name that is unique in the context of the flow cell.
Further flow cells can have a primary and/or secondary barcode (or no barcode at all).
These are the barcode that can be used for demultiplexing of the library.
This can either refer to an barcode from an existing barcode set but it is also possible to specify a custom sequence for ad-hoc definition of barcodes.
Each library is also specified to be loaded on one or more lines.
Of course, each barcode (or barcode combination in the case of dual sequencing) can only occur once on each lane as demultiplexing would not be possible otherwise.
Obviously, different libraries can use the same barcode sequence if they are loaded on different lanes.

-----------------
Cycle Information
-----------------

When starting the machine, the operator provides a certain program with cycle information to the machine.
This specifies how many reads are created and whether a read is a template, an index barcode, or a molecular barcode.
Some examples are given below (the commas can be omitted).

- ``150T,10B,10B,150T`` -- 150 template bases, 10 barcode bases, 10 barcode bases, 150 template bases,
- ``75T,10B,75T`` -- 75 template base, 10 barcode bases, 75 template bases,

This information can be overriden for the whole flow cell.
E.g., if you have a flow cell that contains single-cell data, the second case might call for the following:

- ``8M,2S,65T,10B,75T`` -- 8 molecular barcode bases, skip next 2 read bases, 65 template bases, 10 barcode basese, 75 template bases.

You can also override this information oin a per-library fashion.
That is, you can mix libraries from different single-cell platforms.
It is also possible to mix data from exome sequencing and low-input protocols such as Agilent SureSelectXT where the molecular barcode might be ligated in the same read position as the index barcode read in the exome library.
This enables the efficient use of the ever-increasing sequencing capacity by using a high degree of multiplexing.
