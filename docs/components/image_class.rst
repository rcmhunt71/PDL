
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

==================== ================================
   Property           Data Type
==================== ================================
Image Name           String
-------------------- --------------------------------
Description          String
-------------------- --------------------------------
Page URL             String - URL
-------------------- --------------------------------
Reference URL        String - URL
-------------------- --------------------------------
Author               String
-------------------- --------------------------------
Model                String
-------------------- --------------------------------
DL Time              DeltaTime Object
-------------------- --------------------------------
Disk Locations(s)    List of Strings: PATH(S)
-------------------- --------------------------------
Download Status      ENUM (DOWNLOAD, EXIST, ERROR)
-------------------- --------------------------------
Modification Flag    ENUM (NEW, UPDATED, DELETE)
==================== ================================

