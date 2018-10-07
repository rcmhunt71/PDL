==========================
Command-Line Arguments
==========================

Implementation
~~~~~~~~~~~~~~~~~

* Use argpargse module.
* Use option subgroup organization.
* If no subgroup args are specified, show the help screen.

* **All** arguments require:

  * POSIX-style argument structure
  * Description of purpose
  * Default value where necessary


Arguments
~~~~~~~~~~~~~~~~~

Group: Downloads (dl)
=======================
=============== ============ ========================== =============================
**Full option** **Shortcut** **ArgType**                **Description**
--------------- ------------ -------------------------- -----------------------------
<URLs>                       <space separated list>     List of URLs to download
--------------- ------------ -------------------------- -----------------------------
--file          -f           <DL FILE> (file spec)      Redownload images listed in file
=============== ============ ========================== =============================


Group: Duplicates (dups)
==========================
=============== ============ ========================== =============================
**Full option** **Shortcut** **ArgType**                **Description**
--------------- ------------ -------------------------- -----------------------------
--remove_dups   -x           Bool                       Deletes identified duplicates, based on smallest or most recent.
                             (**True**)
=============== ============ ========================== =============================


Group: Inventory (inv)
=======================
=============== ============ ======================== =============================
**Full option** **Shortcut** **ArgType**              **Description**
--------------- ------------ ------------------------ -----------------------------
<file_spec>                   <path filespec> * = ALL  Lists inventory (filespec); reg exp accepted
=============== ============ ======================== =============================


Group: Information (info)
=========================
=============== ============ ======================== =============================
**Full option** **Shortcut** **ArgType**              **Description**
--------------- ------------ ------------------------ -----------------------------
<image>                      String: <image name>     Lists inventory (filespec); reg exp accepted
=============== ============ ======================== =============================


Group: General
==================
=============== ============ ======================= =============================
**Full option** **Shortcut** **ArgType**             **Description**
--------------- ------------ ----------------------- -----------------------------
--cfg           -c            Str: <filespec>        Configuration File
--------------- ------------ ----------------------- -----------------------------
--debug         -d           Boolean (**True**)      Enable Debug Statements
--------------- ------------ ----------------------- -----------------------------
--help          -h           Boolean (**True**)      Detail list of options
=============== ============ ======================= =============================

