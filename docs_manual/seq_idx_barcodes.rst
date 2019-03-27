.. _seq_idx_barcodes:

========
Barcodes
========

Clicking the little "barcodes" icon on the left-hand button bar takes you to the Barcode (Set) Management Section.

----------------
Barcode Set List
----------------

On the barcode set list page, you can see the table with all barcode sets registered for the given site.
For each bacode set, the creation date, name, short name, and desdription is shown.
Clicking on the barcode set's name leads to the detail page of the barcode set.
The little gray button next to each entry gives access to updating and deleting barcode sets.
A confirmation dialogue will be displayed before actually deleting the record from the database.
Note that deleting a barcode set is a permanent action that cannot be undon.
Use the blue "Barcode Set Operations" button on the top right to access functionality for creating new barcode sets.

.. _barcode_set_details:

-------------------
Barcode Set Details
-------------------

On the barcode set details page, you see two tabs "Properties" and "Barcodes".
"Properties" displays the barcode set properties and "Barcodes" that shows the list of all barcodes in this barcode set.

The "Properties" tab shows the following information for each barcode set:

UUID
    The internal identifier used by Digestiflow for identifying the barcode set.
    This value is only used internally by the Digestiflow system.

Created
    The creation time of the barcode set in the database.

Last Modified
    The last modification time of the barcode set record in the database.

Name
    The name of the barcode set, e.g., "Agilent SureSelect Human All Exon V6".

Short Name
    A short name of the barcode set that is displayed together with the barcode name in flow cell visualizations.

Description
    A potentially longer description of the barcode set.

Type
    Either the type "generic" for normal barcode sequence or "10x Genomics Barcode" for 10x Genomics-style comma-separated barcode lists.

The "Barcodes" tab displays a table showing the following for each barcode.

Name
    The primary barcode name, e.g., ``D501``.

Aliases
    An optional, comma-separated list of name aliases.
    E.g., you could use ``501``, ``1``, or ``501,1`` if the name is ``D501`` and you are getting wet-lab Excel sample sheets using ``501`` and ``1`` for the identification of the barcode.

Sequence
    The barcode sequence (in forward orientation as in the kit documentation for Illumina dual index workflow A).
    In the case of 10X Genomics style barcodes, this can be a list of comma-separated barcodes.

---------------------
Updating Barcode Sets
---------------------

The page for updating a barcode has two Tabs: "Properties" and "Barcodes".
In the "Properties" tab you can update the basic properties of the barcode set such as its name.
The "Barcodes" tab shows a spreadsheet-like view for updating the barcodes.
In case of any display errors of the barcodes spreadsheet table simply click on the top-left cell which should make the spreadsheet table redraw properly.
The table has a column for each of the barcode properties listed in :ref:`barcode_set_details`.
The last column indicates whether the row was changed, added, or is to be removed when saving.

Note that the table component behaves similar to spreadsheet software such as Excel in that you select ranges, drag down the current selection on the lower-right corner to copy its values or first select a range and then pasting (Ctrl+V) a copy of the current clipboard value to all selected cells.
You can also copy a range of cells in another spreadsheet program such as Excel, select a cell in the Digestiflow barcode spreadsheet and then insert the cells there.
In the case that the table has too few rows, new rows will be added automatically.
Empty lines at the bottom are ignored.

Also note that various actions such as copying, pasting, inserting rows, and reverse-complementing the selected barcode sequences is available in the context menu.
Simply right-click on any cell to show the context menu.

Do not forget to click "Save" for applying your changes.
