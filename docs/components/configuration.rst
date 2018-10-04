
Configuration
===============

Requirements
-------------

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

Instantiation
-----------------

1) Path to file (required)
2) Specific section to load (optional)

.. _YAML: https://martin-thoma%20.com/configuration-files-in-python/
