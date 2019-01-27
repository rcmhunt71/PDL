import os
import pickle

from PDL.engine.images.image_info import ImageData
from PDL.engine.images.status import DownloadStatus
from PDL.engine.inventory.base_inventory import BaseInventory
from PDL.logger.logger import Logger

import prettytable

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

    def __init__(self, base_dir, metadata=None, serialization=False, binary_filename=None):
        self.base_dir = base_dir
        self.metadata = metadata
        self.pickle_fname = binary_filename
        self.serialize = serialization
        super(FSInv, self).__init__()

    def get_inventory(self, from_file=None, serialize=None, scan_local=True):
        serialize = self.serialize if serialize is None else serialize
        from_file = self.serialize if from_file is None else from_file

        if not self._inventory:
            self.scan_inventory(serialize=serialize, from_file=from_file, scan_local=scan_local)

        return self._inventory

    def scan_inventory(self, scan_local=True, serialize=None, from_file=None, filename=None):
        """
        Aggregate the inventory, and include previous inventory if requested.

        :return: None

        """
        serialize = self.serialize if serialize is None else serialize
        from_file = self.serialize if from_file is None else from_file
        pickle_fname = self.pickle_fname if filename is None else filename

        log.debug("Serialize data: {0}".format(str(serialize)))
        log.debug("Read from file: {0}".format(str(from_file)))

        if from_file:
            log.info("Reading inventory from {0}".format(self.pickle_fname))
            self._inventory = self.unpickle(filename=pickle_fname)

        if scan_local:
            log.debug("Scanning local inventory.")
            self._scan_(base_dir=self.base_dir)

        if serialize:
            log.info("Writing inventory to {0}".format(pickle_fname))
            self.pickle(data=self._inventory, filename=pickle_fname)

            # TODO: Include size of file written

    def pickle(self, data, filename):
        log.debug("Pickling inventory to {0}".format(filename))
        with open(filename, "wb") as PICKLE:
            pickle.dump(data, PICKLE)
        log.debug("Pickling inventory complete")

    def unpickle(self, filename):
        data = dict()
        if os.path.exists(filename):
            with open(filename, "rb") as PICKLE:
                data = pickle.load(PICKLE)
            self._inventory.update(data)
        else:
            log.warn("Unable to find/open '{0}' for reading serialized data.".format(filename))
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
        try:
            contents = os.listdir(directory)
        except FileNotFoundError as exc:
            log.error("Unable to find directory: {0}".format(directory))
            return

        files = [str(x).rstrip(self.INV_FILE_EXT) for x in contents if x.endswith(self.INV_FILE_EXT)]
        directories = [str(x) for x in contents if '.' not in x]

        # Iterate through the files, populating/updating the _inventory dictionary.
        log.debug("\t+ {0}".format(base_dir))
        for file_name in files:
            self._add_imagedata_object(file_name)

            # If metadata was defined/provided
            image_obj = self._inventory[file_name]
            if base_dir not in getattr(image_obj, ImageData.LOCATIONS):
                if self.metadata:
                    if base_dir.lower().endswith(tuple([x.lower() for x in self.metadata])):
                        for meta in self.metadata:
                            if base_dir.lower().endswith(meta.lower()):
                                getattr(image_obj, ImageData.CLASSIFICATION).append(meta)
                                getattr(image_obj, ImageData.LOCATIONS).append(base_dir)

                    # Directory did not match metadata, so add new location
                    else:
                        getattr(self._inventory[file_name], ImageData.LOCATIONS).append(base_dir)

                # No metadata provided... just store location
                else:
                    getattr(self._inventory[file_name], ImageData.LOCATIONS).append(base_dir)

        # Iterate through the directories
        for directory in directories:
            directory = os.path.join(str(base_dir), str(directory))
            self._scan_(target_dir=directory)

    def _add_imagedata_object(self, file_name):
        """
        Used to initialize each dictionary entry in _inventory with an ImageData object
        :param file_name: Image to add to _inventory

        :return: None

        """
        if file_name not in self._inventory:
            self._inventory[file_name] = ImageData()
            setattr(self._inventory[file_name], ImageData.DL_STATUS, DownloadStatus.DOWNLOADED)
            setattr(self._inventory[file_name], ImageData.FILENAME, file_name)

    def list_duplicates(self):
        """
        List duplicate images in the inventory (found in 2+ locations)

        :return: None

        """
        duplicates = dict([(name, obj) for name, obj in self._inventory.items()
                           if len(getattr(obj, ImageData.LOCATIONS)) > 1])
        log.info("DUPLICATES: {0}".format(len(duplicates.keys())))
        for name, image_obj in duplicates.items():
            log.info("{0}: {1}".format(name, ", ".join(getattr(image_obj, ImageData.CLASSIFICATION))))
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
        for index, (name, data) in enumerate(sorted(self._inventory.items())):
            row = [index, name]
            for meta in sorted(self.metadata):
                row.append('X' if meta in getattr(data, ImageData.CLASSIFICATION) else '')
            row.append(', '.join(getattr(data, ImageData.LOCATIONS)) if
                       getattr(data, ImageData.LOCATIONS) != [] else '')
            table.add_row(row)

        # Add the column headers at the bottom of the table for large tables
        if len(self._inventory) > extra_header:
            table.add_row(table.field_names)

        # Return string representation of the table.
        return table.get_string()
