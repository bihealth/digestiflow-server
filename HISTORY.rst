.. _history:

===================
History / Changelog
===================

----------
Unreleased
----------

- Upgrade to SODAR Core v0.10.10 and Django v3.2 (#76).
- Remove local legacy ``tokens`` app, use app from SODAR Core instead.
- Enable Siteinfo app.

------
v0.3.6
------

- Fixing broken search.

------
v0.3.5
------

- Fixing execution of Celery tasks (#72).

------
v0.3.4
------

- Fixing scheduling of Celery tasks (#72)

------
v0.3.3
------

- Various fixes, related to Docker deployment.
- Dependency bump, including upgrade to sodar-core v0.8.0.

------
v0.3.0
------

- Allowing to filter flow cells by status (#51).
- Fixing issue when only barcode sequence was entered.
- Fixing JS issue with superuser support.
- Fixing issue when parsing bases mask.
- Warning if barcode to short for demux instructions.
- Fixing i5 kit display (#57).
- Fixing ``None`` barcode read (#56).
- Adding citation (#53).
- Validator interprets library demux reads (#58).
- Do not look for adapters that have an "N".
- Making save warning message not display on missing sheets.
- Some display improvements.

------
v0.2.0
------

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
- Updating dependencies.
- Making lane information required (#39).
- Hovering BCL adapters highlights similar ones.

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

