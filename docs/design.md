# Logging
## Structure
1) **Import** - simple, single import
1) **Instantiation**
   1) Single instantiation per class/module
      1) Determine call/import path -  lib1.mod1.class.method() --> logger node (based from root)
      1) Path cached per library - improve/maintain speed of logging
      1) Filename: node level plus all children
      1) Set log level - Default: INFO 
 1) **Format**
    1) Field based.
    1) Fields
       1) Timestamp
       1) module
          1) module path
          1) routine
       1) File name
       1) Line number 
          1) Will be 1 frame lower than determination line (want calling line, not invoked line)
       1) Log level 
          1) Text
          1) Numerical
       1) msg 
     1) **EXAMPLE** - MMDDYY-HH:MM:SS - \[log_level_text:line_number]:\[module path]:\[filename:linenumber] - MSG
 1) **Adapters**
    1) Screen
    1) File
       1) Generic file adapter
    1) Stream?  
