
Image Data Class
========================

Scope
--------------
* Should only store data/state.

  * Do not process anything (downloading, sorting, etc.)

* Should store state: SUCCESS, EXISTS, ERROR (Multiple Error Types).

  * States should be enumerated as CONSTANTS.

* Constants should be stored in separate object within Object file.

Instantiation
---------------------------
* Ability to initialize from data store. E.g. - class method.
* Ability to initialize from code: __init__().


Class Specification
---------------------------
**DATA**

* If image exists, but is missing data, use current instance to fill in
  missing data.


**MODIFICATION**

* Ability to mark object as updated (or put in list, but it should be intrinsic
  to instantiated object).


**STORAGE**

* Ability to deserialize into datastore, or serialize from datastore into
  memory.
* Ability to read/write binary storage of objects (e.g. - pickling).

Attributes
---------------------

=================== ======================= ================================
Attribute           Property Description    Data Type
=================== ======================= ================================
image_name          Image Name              String
------------------- ----------------------- --------------------------------
description         Description             String
------------------- ----------------------- --------------------------------
page_url            Page URL                String - URL
------------------- ----------------------- --------------------------------
image_url           Image URL               String - URL
------------------- ----------------------- --------------------------------
author              Author                  String
------------------- ----------------------- --------------------------------
subject             Subject Of Image        String
------------------- ----------------------- --------------------------------
downloaded_on       Downloaded On           Datetime Object
------------------- ----------------------- --------------------------------
download_dur        Download Duration (sec) DeltaTime Object
------------------- ----------------------- --------------------------------
locations           Disk Locations(s)       List of Strings: PATH(S)
------------------- ----------------------- --------------------------------
dl_status           Download Status         ENUM (PENDING, DOWNLOADED, EXISTS, ERROR)
------------------- ----------------------- --------------------------------
mod_status          Modification Flag       ENUM (NEW, UPDATED, DELETE)
=================== ======================= ================================

