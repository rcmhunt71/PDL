
References:
-----------

-  `MD Article 1`_
-  `RST Article 1`_

   -  `Referencing other files`_
   -  `PyCharm Support`_


Logging
----------

Structure
==========

1) **Import** - simple, single import
2) **Instantiation**

   1) Single instantiation per class/module

      1) Determine call/import path - lib1.mod1.class.method() –> logger
         node (based from root)
      2) Path cached per library - improve/maintain speed of logging
      3) Filename: node level plus all children
      4) Set log level - Default: INFO

3) **Format**

   1) Field based.
   2) Fields

      1) Timestamp
      2) module

         1) module path
         2) routine

      3) File name
      4) Line number

         1) Will be 1 frame lower than determination line (want calling
            line, not invoked line)

      5) Log level

         1) Text
         2) Numerical

      6) msg

   3) **EXAMPLE** - MMDDYY-HH:MM:SS -
      [log_level_text:line_number]:[module path]:[filename:linenumber] -
      MSG

4) **Adapters**

   1) Screen
   2) File

      1) Generic file adapter

   3) Stream?

Configuration
----------------

Requirements
=============

1) **Load from file**

   1) **FILE #1**: URL, site configuration, regexps (or regexp file to
      be loaded)
   2) **FILE #2**: Application settings

2) **Human Readable/Configurable**

   1) Recommend `YAML`_ for complex configuration files (requires
      pyYaml)
   2) Highest level should be the section label

      ::

            section1:
               key1: value1
               key2: value2
            section2:
               key1: value1
               key2: 
                 - value2a
                 - value2b
                 - value2c

3) Need following abilities:

   1) List sections (highest level options)
   2) Cast values as needed: x.get(valueType)

      ::

         x.get(string) 
         x.get(int)

   3) Get entire section
   4) Display entire file
   5) Debug/logging capability
   6) Catchable exception if unable to:

      1) Find File
      2) Read File

**Instantiation**
-----------------

1) Path to file (required)
2) Specific section to load (optional)

Command-line Arguments
======================

Package Structure and Hierarchy
===============================

Image Object
============

Elements
--------

Datastore (Abstraction)
=======================

Download Abstraction (non-tool specific)
========================================

Object Scopes
=============

.. _configuration-1:

Configuration
-------------

Image Objects
-------------

.. _logging-1:

Logging
-------

.. _MD Article 1: https://help.github.com/articles/basic-writing-and-formatting-syntax/
.. _RST Article 1: https://gist.github.com/dupuy/1855764
.. _Referencing other files: https://stackoverflow.com/questions/37553750/how-can-i-link-reference-another-rest-file-in-the-documentation
.. _PyCharm Support: https://www.jetbrains.com/help/pycharm/restructured-text.html
.. _YAML: https://martin-thoma%20.com/configuration-files-in-python/
