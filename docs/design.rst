### References:
* [MD Article 1](https://help.github.com/articles/basic-writing-and-formatting-syntax/)
* [RST Article 1](https://gist.github.com/dupuy/1855764)
   * [Referencing other files](https://stackoverflow.com/questions/37553750/how-can-i-link-reference-another-rest-file-in-the-documentation)
   * [PyCharm Support](https://www.jetbrains.com/help/pycharm/restructured-text.html)
   

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


# Configuration
## Requirements
1) **Load from file**
   1) **FILE #1**: URL, site configuration, regexps (or regexp file to be 
   loaded)
   1) **FILE #2**: Application settings
   
1) **Human Readable/Configurable**
   1) Recommend [YAML](https://martin-thoma
   .com/configuration-files-in-python/) for complex configuration files 
   (requires pyYaml)
   1) Highest level should be the section label

             section1:
                key1: value1
                key2: value2
             section2:
                key1: value1
                key2: 
                  - value2a
                  - value2b
                  - value2c
            
  1) Need following abilities:
     1) List sections (highest level options)
     1) Cast values as needed: x.get(valueType) 

            x.get(string) 
            x.get(int)

     1) Get entire section
     1) Display entire file
     1) Debug/logging capability
     1) Catchable exception if unable to:
        1) Find File
        1) Read File 

## **Instantiation**
   1) Path to file (required)
   1) Specific section to load (optional)


# Command-line Arguments

# Package Structure and Hierarchy

# Image Object
## Elements

# Datastore (Abstraction)

# Download Abstraction (non-tool specific)

# Object Scopes
## Configuration
## Image Objects
## Logging
