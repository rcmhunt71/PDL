import os
import pickle

import prettytable
from PDL.configuration.properties.app_cfg import (
    AppCfgFileSections, AppCfgFileSectionKeys, ProjectCfgFileSectionKeys, ProjectCfgFileSections)
from PDL.engine.inventory.base_inventory import BaseInventory
from PDL.logger.logger import Logger

log = Logger()

# TODO: Add doctstrings


class FSInv(BaseInventory):
    """
    Aggregates file storage inventory in a dictionary.
    Minimum: key = image name, value = locations
    If metadata is provided (stored in directories by category), it can check the location, and if matches
    the metadata, it will create a flag (rather than store the location for that instance of the image)
    """

    INV_FILE_EXT = ".jpg"
    DATA_FILE_EXT = ".dat"
    DIRS = 'dirs'

    def __init__(self, base_dir, cfg_info=None, metadata=None, serialization=False):
        self.base_dir = base_dir
        self.metadata = metadata
        self.cfg_info = cfg_info
        self.pickle_fname = self._build_pickle_filename()
        self.serialize = serialization
        super(FSInv, self).__init__()

    def get_inventory(self, from_file=None, serialize=None, scan_local=True):
        serialize = self.serialize if serialize is None else serialize
        from_file = self.serialize if from_file is None else from_file

        if not self._inventory:
            self.scan_inventory(serialize=serialize, from_file=from_file, scan_local=scan_local)

        return self._inventory

    def scan_inventory(self, scan_local=True, serialize=None, from_file=None):
        """
        Aggregate the inventory, and include previous inventory if requested.

        :return: None

        """
        serialize = self.serialize if serialize is None else serialize
        from_file = self.serialize if from_file is None else from_file

        log.debug("Serialize data: {0}".format(str(serialize)))
        log.debug("Read from file: {0}".format(str(from_file)))

        if from_file:
            log.info("Reading inventory from {0}".format(self.pickle_fname))
            self._inventory = self._unpickle(filename=self.pickle_fname)

        if scan_local:
            log.debug("Scanning local inventory.")
            self._scan_(base_dir=self.base_dir)

        if serialize:
            log.info("Writing inventory to {0}".format(self.pickle_fname))
            self._pickle(data=self._inventory, filename=self.pickle_fname)

    def _build_pickle_filename(self):
        location = self.cfg_info.app_cfg.get(AppCfgFileSections.LOGGING,
                                             AppCfgFileSectionKeys.JSON_FILE_DIR)
        dl_drive = self.cfg_info.app_cfg.get(AppCfgFileSections.LOGGING,
                                             AppCfgFileSectionKeys.LOG_DRIVE_LETTER)
        filename = "{0}{1}".format(self.cfg_info.engine_cfg.get(ProjectCfgFileSections.PYTHON_PROJECT,
                                                                ProjectCfgFileSectionKeys.NAME).upper(),
                                   self.DATA_FILE_EXT)

        # Check if location exists, create if requested
        location = os.path.sep.join([location, filename])
        if dl_drive is not None:
            location = "{drive}:{dl_dir}".format(drive=dl_drive.strip(":"), dl_dir=location)
            log.debug("Updated data directory for drive letter: {0}".format(location))
        log.debug("Inventory Data File: {0}".format(location))
        return location

    def _pickle(self, data, filename):
        log.debug("Pickling inventory to {0}".format(filename))
        with open(filename, "wb") as PICKLE:
            pickle.dump(data, PICKLE)
        log.debug("Pickling inventory complete")

    def _unpickle(self, filename):
        data = dict()
        if os.path.exists(filename):
            with open(filename, "rb") as PICKLE:
                data = pickle.load(PICKLE)
            self._inventory.update(data)
        else:
            log.error("Unable to find/open '{0}' for reading serialized data.".format(filename))
        return data

    def _scan_(self, target_dir=None, base_dir=None):
        """
        Recursively determine the images and directories. Store the information about the image
        in the _inventory dictionary, then traverse the sub-drectories.

        :param target_dir: Used by recursive call.
        :param base_dir: Starting point for scanning

        :return: None

        """
        # Determine current location to start scan (based on current place in recursion)
        directory = target_dir or self.base_dir
        if base_dir is None and target_dir is None:
            base_dir = self.base_dir
        elif base_dir is None:
            base_dir = target_dir

        log.debug("Scanning Base Dir: {0}".format(base_dir))

        # Get the list of files and directories
        contents = os.listdir(directory)
        files = [str(x).rstrip(self.INV_FILE_EXT) for x in contents if x.endswith(self.INV_FILE_EXT)]
        directories = [str(x) for x in contents if '.' not in x]

        # Iterate through the files, populating/updating the _inventory dictionary.
        log.debug("\t+ {0}".format(base_dir))
        for file_name in files:
            self._create_entry_structure(file_name)

            # If metadata was defined/provided
            if self.metadata:
                if base_dir.lower().endswith(tuple([x.lower() for x in self.metadata])):
                    for meta in self.metadata:
                        if base_dir.lower().endswith(meta):
                            self._inventory[file_name][meta] = True
                            self._inventory[file_name][self.DIRS].append(base_dir)

                # Directory did not match metadata, so add location
                else:
                    self._inventory[file_name][self.DIRS].append(str(directory))

            # No metadata provided... just store location
            else:
                self._inventory[file_name][self.DIRS].append(str(directory))

        # Iterate through the directories
        for directory in directories:
            directory = os.path.join(str(base_dir), str(directory))
            self._scan_(target_dir=directory)

    def _create_entry_structure(self, file_name):
        """
        Used to initialize each dictionary entry in _inventory
        :param file_name: Element to add to _inventory

        :return:None

        """
        if file_name not in self._inventory:
            self._inventory[file_name] = {self.DIRS: []}

    def list_duplicates(self):
        """
        List duplicate images in the inventory (found in 2+ locations)

        :return: None

        """
        duplicates = dict([(k, v) for k, v in self._inventory.items() if len(v[self.DIRS]) > 1])
        log.info("DUPLICATES: {0}".format(len(duplicates.keys())))
        for name, image in duplicates.items():
            log.info("{0}: {1}".format(name, image))
        log.info("TOTAL FILES ANALYZED: {0}".format(len(self._inventory.keys())))

    def list_inventory(self):
        """
        Create pretty table based on _inventory.,

        Header:
        | Index | Name | <column per metadata> | Location |

        :return: String representation of the table

        """
        extra_header = 1000

        table = prettytable.PrettyTable()

        # Set up the headers
        header = ['Index', 'Name']
        header.extend([x.capitalize() for x in sorted(self.metadata)])
        header.append('Locations')
        table.field_names = header

        # Define the column alignments
        table.align['Index'] = 'r'
        table.align['Name'] = 'l'
        table.align['Locations'] = 'l'
        for x in sorted(self.metadata):
            table.align[x.capitalize()] = 'c'

        # Populate the table
        for index, (name, data) in enumerate(self._inventory.items()):
            row = [index, name]
            for meta in sorted(self.metadata):
                row.append('X' if meta in data else '')
            row.append(', '.join(data[self.DIRS]) if data[self.DIRS] != [] else '')
            table.add_row(row)

        # Add the column headers at the bottom of the table for large tables
        if len(self._inventory) > extra_header:
            table.add_row(table.field_names)

        # Return string representation of the table.
        return table.get_string()
