REQUIREMENTS:
-------------

This are the **identified** requirements for each piece of the process.
This document will be used to determine the required architecture,
classes, interfaces, and restrictions.

SELECT URLS
-----------

1. Verify URLs are token-delimited (space)

   1. Split if https:// is found in the middle of the string.
   2. Debug log that action is occurring.
   3. Debug log any records that were acted on.

2. Remove duplicates from list

   1. Cast: ``list(set(url_list))``

      1. Debug log how many duplicates were found
      2. Debug log which urls were duplicates?

DETERMINE IMAGE URL
-------------------

1. Find largest image URL

DOWNLOAD IMAGE
--------------

1. Determine if image has been downloaded:

   1. Locally:

      1. Check local file system

   2. Remotely:

      1. Data repository of images
      2. Download image to local storage
      3. Parallel downloads
      4. Record time per DL

2. Monitor and report status

   1. ERROR or TIMEOUT: retry
   2. Backoff retry mechanism

STATISTICS
----------

1. Number of duplicates in the DL list
2. Number of splits in the DL list?
3. Number of Images:

   1. Downloaded
   2. Skipped

      1. Local
      2. Remote

   3. Errored
   4. Total time to download
   5. Avg time to download

CLI
---

1. Dry-run
2. Utilities execution
3. Help screens and logical options/descriptions
4. Specify logging level
5. Mount-check for specific options

OUTPUT
------

1. Log to screen (debug or info)
2. Log to file
3. Create summary file per execution

   1. Unique filename
   2. Replay ability
   3. Store in common directory

DATA REPOSITORY
---------------

1. Autostart service if not running
2. Persistent
3. Data Fields

   1. Image Name
   2. Image URL
   3. Web URL
   4. Photographer
   5. Size
   6. Storage Locations
   7. Subject Name
   8. DL Date

UTILITIES
---------

1. Data Repository \| Disk Sync
2. Duplicate Check
3. Stats generator
4. Log \| Data sync
5. Report generation

VISUAL CLASSIFICATION/SORTING
-----------------------------

1. Classifications
2. Locations
3. Viewer

   1. Zoom
   2. Panels
   3. Options

UNIT TESTS
----------

1. PyTest

   1. Coverage Metrics
   2. Mocks

REPOSITORIES
------------

1. `PDL`_

INSTALLATION:
-------------

1. pip installable

.. _PDL: https://github.com/rcmhunt71/PDL
