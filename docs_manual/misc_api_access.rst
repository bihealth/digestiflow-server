.. _misc_api_access:

==========
API Access
==========

Digestiflow Web provides an API for managing all objects within a site: Sequencers, barcode sets, barcodes, flow cells, libraries, and messages with attachments.
Generally, the API is available with the prefix ``/api``.

The Digestiflow REST API is implemented using Django REST Framework which also allows for the easy exploration of the API in your browser.
The same URLs that you can access in your browser can also be accessed by API clients or ``curl`` but will not render HTML pages but return JSON data.

.. note::
    The Digestiflow REST API has not stabilized yet.
    The current version is considered to be "v0".
    After stabilizing as "v1.0", the API will use semantic versioning.

--------------
First Examples
--------------

The following assume you already have a first site, sequencer, barcode set, and flow cell setup already.

1. Quickly access the API by going to the detail view of your flow cell, click the blue "Flow Cell Operations" button and select "JSON export".
   The resulting output already! comes from the Digestiflow REST API.

2. Go to the flow cell list of your site.
   Copy the full URL and insert ``/api`` between the host name and ``/flowcells`` (*).
   From here, you can explore the API for managing flow cells.

3. Create an API token and copy it somewhere safe.
   You can now use the following ``curl`` command.
   ``$URL`` is the result of (*) in the example 2 and ``$TOKEN`` is the token.

   ::
        # XXX
        $ curl -H "Token: bearer $TOKEN" "$URL"

--------------
Authentication
--------------

In the examples above you have already seen the two modes of authentication that Digestiflow REST API supports.

1. Use the browser cookie after logging into Digestiflow with a browser.
2. Use an API token with an appropriate header showing the API token to the server.

------------------
Object Identifiers
------------------

For understanding the API, you need to know that Digestiflow uses UUID keys (random strings, e.g., ``3d4b6d4f-62a7-4534-9a08-b473adae7302``) for access.
Each object has such an ID, including each site.

------------
API Patterns
------------

Generally, the basic API URLs have the following format (where ``site`` and ``object`` specify UUIDs):

1. ``/api/<object type>/<site>/`` (*)
   HTTP GET obtains a list of objects while POST allow to create new ones.
2. ``/api/<object type>/<site>/<object>/``
   HTTP GET obtains the details of the object while POST allows for full updates, PUT allows for partial updates, DELETE allows deletion.

The easiest way to learn about the API is to navigate to the URL of type 1 (*) with your browser and explore it from here.

-----------------------
Available API Endpoints
-----------------------

``/api/sequencers/<site>/``
    List sequencers or create new one in site.

``/api/sequencers/<site>/<sequencer>``
    Fetch, update, or delete sequencer.

``/api/sequencers/by-vendor-id/<site>/<vendor ID>``
    Lookup sequencer by its vendor ID.

``/api/barcodesets/<site>/``
    List barcode set or create new one in site.

``/api/barcodesets/<site>/<barcodeset>``
    Fetch, update, or delete barcode set.

``/api/barcodesetentries/<site>/<barcodeset>/``
    List barcode set or create new barcode in barcode set.

``/api/barcodesetentries/<site>/<barcodeset>/<barcode>``
    Fetch, update, or delete barcode.

``/api/barcodesetentries/retrieve/<site>/<barcode>``
    Fetch barcode using UUID without knowing its barcode set.

``/api/flowcells/<site>/``
    List flow cell or create new one in site.

``/api/flowcells/<site>/<flowcell>``
    Fetch, update, or delete flow cell.

``/api/flowcells/resolve/<site>/<sequencer vendor ID>/<run no>/<flowcell vendor ID>``
    Fetch flow cell (run) from sequencer vendor ID, run number, and flow cell vendor ID.

``/api/indexhistos/<site>/<flowcell>/``
    List index histogram records or create new one for flow cell.

``/api/indexhistos/<site>/<flowcell>/<indexhistogram>``
    Fetch, udpate, or delete single index histogram record.

``/api/messages/<site>/<flowcell>/``
    List messages or create new one for flow cell.

``/api/messages/<site>/<flowcell>/<message>/``
    Fetch, update, or delete message.

``/api/attachments/<site>/<flowcell>/<message>/``
    List message attachments or create new one for message.

``/api/messages/<site>/<flowcell>/<message>``
    Fetch, update, or delete attachments.
