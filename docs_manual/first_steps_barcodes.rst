.. _first_steps_barcodes:

============================
Tutorial: Configure Barcodes
============================

Clicking the "Barcodes" entry in the green menu on the left-hand brings you to the barcode sets overview of your site.
This allows for managing barcode (index adapter sequence) sets in your site that you can reuse.
You can then refer to these barcodes by their name (or number) and thus simplify the error-prone copy-and-paste step of copying adapter sequences around.

Managing barcodes is similar to managing sequencers.
First, click the blue "Barcodes Operation" on the top right and then "Create".

Fill in the basic properties of the barcode set in the "Properties" page.
Then, click the "Barcodes" tab and into the first cell of the first row.
You can now enter (or better: copy and paste) your barcodes from a spreadsheet or your kit vendor's manual.

The columns are as follows:

name
    The primary name of the adapter, e.g., ``A001``.
aliases
    An optional, comma-separated list of adapters names, e.g., ``1,01,001``.
sequence
    The adapter sequence.
    Note that you always enter the **forward** adapter sequence in Digestiflow.
    In the case of dual indexing, Digestiflow Demux will automatically reverse-complement the adapter sequence if necessary for the dual indexing workflow of your sequncing device.
status
    This field is updated by the barcode editor and indicates whether the current row is added or changed.

Note that a context menu is available, e.g., for quickly reverse-complementing bases.

After completely filling out the barcode set table, continue by clicking the blue "Create" on the top right of the form.
The detail screen of a barcode set offers a blue "Barcode Set Operations" button which gives access to creating new barcode sets, updating or deleting the current one, or creating a JSON data export.
