.. _seq_idx_sequencers:

==========
Sequencers
==========

Clicking the little "sequencers" icon on the left-hand button bar takes you to the Sequencer Mangement Section.

--------------
Sequencer List
--------------

On the sequencer list page, you can see table with all sequencers.
For each sequencer, the creation date, vendor ID, label, number of runs, and short description is show.
Clicking on a sequencer's vendor ID leads to the detail page of the sequencer.
The little gray button next to each entry gives access to updating and deleting sequencers.
A confirmation dialogue will be displayed before actually deleting the record from the database.
Note that deleting a sequencer is a permanent action that cannot be undone.
Use the blue "Sequencer Operations" button on the top right to access functionality for creating new sequencers.

-----------------
Sequencer Details
-----------------

On the sequencer details page, you see two tabs.
"Properties" displays the sequencer properties and "Flow Cells/Runs" that shows a list of all runs of this particular sequencer.
Use the blue "Sequencer Operations" to access functionality for deleting and updating the sequencer.

The "Properties" tab shows the following information for each flow cell:

UUID
    The identifier used by Digestiflow for identifying the sequencer.
    This value is only used by the Digestiflow system.

Site
    The site that the sequencer is in.

Created
    The creation time of the sequencer record in the database.

Last Modified
    The last modification time of the sequencer record in the database.

Vendor ID
    The identifier assigned by Illumina to the sequencing machine.
    This value is part of the run folders (e.g., ``NS501234`` for a NextSeq 500 sequencer).
    **This is the most important configuration value.**

Label
    Short user-defined label for easily identifying the sequencer.
    You can specify any string here.

Description
    An optional, potentially longer description for the sequencer.

Machine Model
    The model of the sequencing machine.
    This value is only used for display of the sequencer in Digestiflow Server.

Slot Count
    The number of slots for flow cells.
    This is equal to the number of flow cells in your sequencer, e.g., ``1`` for NextSeq 500 and ``2`` for HiSeq 4000.
    This value is used for sanity checks when entering data manually into Digestiflow Server.

Dual Indexing Workflow
    The "Illumina dual indexing workflow" to use.
    **This is the second most important parameter.**
    The value will be used for automatically reverse-complementing the i5 barcode adapter when read as the second index read.

    In the case of **Workflow A**, the i5 barcode adapter sequence is read in forward orientation.
    On the case of **Workflow B**, the i5 barcode adapter sequencer is read in reverse orientation.
    In the two sentences above, *forward* and *reverse orientation* are meant with respect to the sequence given in the sequencing chemistry manuals.

    Workflow A is used by NovaSeq 6000, MiSeq, HiSeq 2500, and HiSeq 2000 while workflow B is used by iSeq 100, MiniSeq, NextSeq, HiSeq X, HiSeq 4000, and HiSeq 3000.

    More details can be found `on the Illumina Support website <https://support.illumina.com/downloads/indexed-sequencing-overview-15057455.html>`_.
