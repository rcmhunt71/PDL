Logging
=========

Structure
----------
1) **Import** - simple, single import
2) **Instantiation**

   1) Single instantiation per class/module

      1) Determine call/import path - lib1.mod1.class.method() –> logger
         node (based from root)
      2) Path cached per library - improve/maintain speed of logging
      3) Filename: node level plus all children
      4) Set log level - Default: INFO

3) **Format**

   1) Field Based.
   2) Fields:

      * Timestamp
      * Module

        - module path
        - routine

      * File Name
      * Line Number

        - Will be 1 frame lower than determination line (want calling line, not invoked line)

      * Log Level

        - Text
        - Numerical

      * Transaction ID (UUID or random id?)
      * Message

   3) **EXAMPLE** - MMDDYY-HH:MM:SS

      - \[log_level_text\:line_number]\:\[modulepath]\:\[filename\:\[linenumber]\:\[transId] - MSG

4) **Adapters**

   1) Screen
   2) File

      1) Generic file adapter

   3) Stream?
