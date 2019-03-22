.. _flowcells_details:

===============
Flow Cell Views
===============

Differently from the rest of the manual, we will first describe the flow cell details view as this simplifies the explanation.

-----------------
Flow Cell Details
-----------------

The detail view shows the following information for each flow cell.
This view also highlights errors that were detected in the sample sheet or inconsistencies between the sample sheet and the raw BCL calls.

Note that the messages tab is documented in detail in :ref:`flowcells_messages`.

Properties Tab
==============

XXX TODO XXX

Sample Sheet
============

XXX TODO XXX

Base Call Information
=====================

XXX TODO XXX

--------------
Flow Cell List
--------------

The flow cell list shows a list of all flow cells registered with the system.
The information in each row is relatively dense to allow to get the most relevant information with a single glance and at the same time allow for easily updating the state for flow cells with very few clicks.

The columns are as follows:

Comment / Message / Attachments Indicator
    Whether or not the comment field of the flow cell is filled, messages have been added to the flow cell and/or there are attachments with the messages.

Sequencing Status, Demultiplexing Status, Delivery Status
    The first three columns display little icons for the three different states.
    TODO: more description

Deliver Sequence Conversion and/or Archives with Base Calls
    The next two icons indicate whether sequence conversion is asked and/or archives with the raw base calls are to be generated.

Sequencing Machine
    The name of the sequencing machine.
    Clicking on the name leads to the detail view of the given sequencer.

Run Number
    The sequential number of runs on the given machine.

Slot
    Indication whether the flow cell was run as the first or second flow cell in the instrument.

Flow Cell Vendor ID
    The vendor ID of the flow cell.

Sequencing Date
    Date when the sequencing run was started.

TODO: complete description

The little gray button on the right-hand side of the table rows allows to access the functions for updating and deleting flow cells.

---------------
Updating Status
---------------

When clicking the status icons, a window with a list of button appears.
You can use this for changing the individual state of the flow cell with two clicks.
After selecting the target state, the state will be updated and the row will be updated to reflect the results.
