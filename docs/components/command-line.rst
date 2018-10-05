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

Group: Downloads
==================
=============== ============ ========================== =============================
**Full option** **Shortcut** **ArgType**                **Description**
--------------- ------------ -------------------------- -----------------------------
--download      -d           <comma separated list>     List of URLs to download
=============== ============ ========================== =============================


Group: Duplicates
==================
=============== ============ ========================== =============================
**Full option** **Shortcut** **ArgType**                **Description**
--------------- ------------ -------------------------- -----------------------------
--duplicate     -x           Bool                       Check and list inventory for duplicates
                             (**True**)
--------------- ------------ -------------------------- -----------------------------
--remove_dup    -r           Bool                       Deletes identified duplicates, based on smallest or most recent.
                             (**True**)
=============== ============ ========================== =============================


Group: Inventory
==================
=============== ============ ======================== =============================
**Full option** **Shortcut** **ArgType**              **Description**
--------------- ------------ ------------------------ -----------------------------
--inv           -i           <path filespec> * = ALL  Lists inventory (filespec)
=============== ============ ======================== =============================



Group: General
==================
=============== ============ ======================= =============================
**Full option** **Shortcut** **ArgType**             **Description**
--------------- ------------ ----------------------- -----------------------------
--debug         -D           Boolean (**True**)      Enable Debug Statements
--------------- ------------ ----------------------- -----------------------------
--help          -h           Boolean (**True**)      Detail list of options
=============== ============ ======================= =============================

