.. _history:

===================
History / Changelog
===================

-----------------
HEAD (unreleased)
-----------------

- Fixing rendering error with empty barcodes.
- Fixing email sending (obtaining of address).
- More human-oriented rendering and editing of bases mask strings.
- Update cache when registering new histogram stats (#25).
- Fixing search for messages (#15).
- Fixing but preventing suppression of index errors.
- Using commas in cycle specification in sample sheet (#48).
- Serving attachments as download files (#49).
- Using role assignment in search (#47).
- Updating sentry client library to ``sentry-sdk`` (#50).
- Adding Sentry user feedback form.

------
v0.1.1
------

- Paginating large lists.
- More prefetching for large list for speedups.
- Fixing organism/reference editing.
- More refined checking of barcodes and demultiplexing cycles.
- Properly catching error of duplicate barcode name/sequence in barcode set.
- Reverse-complement sequence search.
- Indicating that no histograms can be expected if no barcode reads exist.
- Bumping dependency on SODAR Core.
- Fixing adapter validation in case of chromium barcodes/barcodes lists.
- Fixing organism input and making error message more clear.
- Fixing manual creation of flow cells.
- Fixing "dirty" in readthedocs manual release PDF.
- Improving detail display and form layout for flow cell.

------
v1.0.0
------

- Initial release.
  Everything is new.

