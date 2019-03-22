.. _flowcells_editor:

================
Flow Cell Editor
================

The update view for flow cells has two tabs.
The "Properties" tab allows to modify the basic attributes of the flow cell.
The properties sequencing date, sequencing machine, slot, flow cell vendor ID and user-defined label are edited by setting the folder name.
Note that you can define a **label override** different from the folder name for display in the flow cell list.

The "Libraries" tab allows for editing the libraries on your flow cell.
The description of its functionality has two steps.
First, we will explain the different components and how you can interact with them.
This will allow you to enter a sample sheet library by library in the form.
In most cases, the data is available in wet lab spreadsheet sample sheets.
Digestiflow Web supports you in performing this task effectively and efficiently.
The second step describes a workflow that the authors have successfully implemented in their daily work.

-----------------
Editing Libraries
-----------------

The libraries editor has the following columns.

Library ID
    The library identifier.

Organism (optional)
    The organism the library was generated from.

i7 Index Barcode Set
    The set of i7 barcodes to use or ``enter your sequence here -->`` if you want to enter a manual barcode.

i7 Barcode
    The i7 barcode sequence if using manually entered sequence.
    Otherwise, the barcode name and sequence will be displayed.
    If the barcode is not known in the barcode set, your cells will have a red background.

i5 Index Barcode Set
    The set of i5 barcodes, cf. "i7 Index Barcode Set" above.

i5 Barcode
    The i5 barcode sequence or barcode, cf. "i5 Barcode" above.

Lanes
    The lanes that the library was loaded on.
    You can mark a library to be loaded on multiple by lanes by using comma-separed lists and/or ranges, e.g., ``1,2,4``, ``1-4``, or ``1-3,5-8``.

Cycle Configuration (Optional)
    Custom per-lane cycle configuration

--------------------
Library Copy & Paste
--------------------

This section describes the efficient workflow for copy-and-paste of data from spreadsheets.

As a prerequisite should have all your barcode sets prepared.
The barcodes should either have the same name used in the sample sheet you are copying from or you should assign appropriate aliases.
We assume that the source spreadsheet has a reasonable structure, e.g., it contains consecutive lines of libraries with separate columsn for sequence names, the i7 and i5 barcode index names, and lane numbers.

1. Copy the column with the library names from the spreadsheet into the library editor.
   For this, select the cell to start inserting into and then either press Ctrl+V or right-lick on the cell and select "paste".
2. Select the appropriate organism from the first row by clicking on the small triangle in the right part of the cell.
   Copy this value.
   Select the cells below the first one down to the one in the same or as the lowermost library name.
   Insert the organism value to fill out all selected fields.
   Adjust this step in case you have different organisms.
3. Select the type of the first barcode (if any) and use the same "copy single value and paste into range" step as in step 2.
   You can selcect ``type your value here -->`` for entering an ad-hoc barcode sequence.
4. Copy and paste the barcode names from your external sample sheet into the table using the same approach as in step 1.
   Note that if you have properly set the name and/or aliases of the barcodes then your barcode names will be automatically replaced by the string ``{barcode name} ({barcode sequence})``.
   In the case that the lookup fails, the affected cells will be marked in red.
   If this does not work (e.g., you selected the wrong barcode set first, pasted non-matching barcode names, and then fixed the barcode set) then you can fix it as follows.
   Select the affected cell(s), right-click, and click "XXX TODO XXX".
   This will re-start the resolution of barcodes from the barcode names.
   Note that lookup only works based on name not sequence.
5. If you have dual indexing then use the same approach as in step 3 for selecting the barcode.
6. Simiarly, use the approach from step 3 for selecting/entering the second barcode.
7. Copy and paste the lane numbers for the library.
8. Optionally assign custom cycle configuration for the library if different from the cycle configuration of the flow cell.

Don't forget to save your changes.

Note that the editor will tolerate certain changes although it warns you by highlighting the fields in red.
You will get warnings in the flow cell detail view.
