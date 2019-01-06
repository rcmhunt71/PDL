import os

import prettytable

from PDL.engine.inventory.base_inventory import BaseInventory
from PDL.logger.logger import Logger

log = Logger()


class FSInv(BaseInventory):
    """
    Aggregates file storage inventory in a dictionary.
    Minimum: key = image name, value = locations
    If metadata is provided (stored in directories by category), it can check the location, and if matches
    the inventory
    """

    FILE_EXT = ".jpg"
    DIRS = 'dirs'

    def __init__(self, base_dir, metadata=None):
        self.base_dir = base_dir
        self.metadata = metadata
        super(FSInv, self).__init__()

    def get_inventory(self):
        self._scan_(base_dir=self.base_dir)

    def _scan_(self, target_dir=None, base_dir=None):
        directory = target_dir or self.base_dir
        if base_dir is None and target_dir is None:
            base_dir = self.base_dir
        elif base_dir is None:
            base_dir = target_dir

        log.info("Base Dir: {0}".format(base_dir))

        contents = os.listdir(directory)
        files = [str(x).rstrip(self.FILE_EXT) for x in contents if x.endswith(self.FILE_EXT)]
        directories = [str(x) for x in contents if '.' not in x]

        log.info("\t+ {0}".format(base_dir))
        for file_name in files:
            self._create_entry_structure(file_name)
            if self.metadata:
                metadata_tuple = tuple([x.lower() for x in self.metadata])
                if base_dir.lower().endswith(tuple(metadata_tuple)):
                    for meta in self.metadata:
                        if base_dir.lower().endswith(meta):
                            self._inventory[file_name][meta] = True
                else:
                    self._inventory[file_name][self.DIRS].append(str(directory))
            else:
                self._inventory[file_name][self.DIRS].append(str(directory))

        for directory in directories:
            directory = os.path.join(str(base_dir), str(directory))
            self._scan_(target_dir=directory)

    def _create_entry_structure(self, file_name):
        if file_name not in self._inventory:
            self._inventory[file_name] = {self.DIRS: []}

    def list_duplicates(self):
        duplicates = dict([(k, v) for k, v in self._inventory.items() if len(v[self.DIRS]) > 1])
        log.info("DUPLICATES: {0}".format(len(duplicates.keys())))
        for name, image in duplicates.items():
            log.info("{0}: {1}".format(name, image))
        log.info("TOTAL FILES ANALYZED: {0}".format(len(self._inventory.keys())))

    def list_inventory(self):
        table = prettytable.PrettyTable()

        header = ['Index', 'Name']
        header.extend([x.capitalize() for x in sorted(self.metadata)])
        header.append('Locations')
        table.field_names = header

        table.align['Index'] = 'r'
        table.align['Name'] = 'l'
        table.align['Locations'] = 'l'
        for x in sorted(self.metadata):
            table.align[x.capitalize()] = 'c'

        for index, (name, data) in enumerate(self._inventory.items()):
            row = [index, name]
            for meta in self.metadata:
                row.append('X' if meta in data else '')
            row.append(', '.join(data[self.DIRS]) if data[self.DIRS] != [] else '')
            table.add_row(row)
        table.add_row(table.field_names)

        return table.get_string()
