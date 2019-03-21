from collections import OrderedDict
import os
from typing import Dict, List

import prettytable

from PDL.app.pdl_config import PdlConfig
from PDL.engine.inventory.inventory_composite import Inventory
from PDL.engine.images.image_info import ImageData
from PDL.logger.logger import Logger
from PDL.logger.utils import num_file_of_type

LOG = Logger()


class NotInventoryClass(Exception):
    pass


class InvStats:
    UNIQUE = 'Unique Images'
    TOTAL = 'Total Images'

    def __init__(self, inventory: Inventory) -> None:
        self.inventory = inventory
        if not isinstance(inventory, Inventory):
            raise NotInventoryClass

    def tally_summary_data(self) -> dict:
        """
        Tallies basic information about inventory

        :return: dictionary of summary stats

        """
        return OrderedDict([
            (self.UNIQUE, len(self.inventory.inventory.keys())),
            (self.TOTAL, sum([len(getattr(x, ImageData.LOCATIONS)) for
                              x in self.inventory.inventory.values()]))
        ])

    def inventory_summary_table(self) -> str:
        """
        Get tallied information and puts into a table.

        :return: Stringified table output

        """
        summary = self.tally_summary_data()

        table = prettytable.PrettyTable()
        table.field_names = ['Inventory Summary', 'Count']
        for k, v in summary.items():
            table.add_row([k, v])
        return table.get_string()

    def get_image_directories(self) -> Dict[str, int]:
        """
        Get a list of the unique directories and their counts

        :return: Dictionary of unique directories and the image counts

        """
        data = {}
        for image_info in self.inventory.inventory.values():
            for loc in getattr(image_info, ImageData.LOCATIONS):
                if loc not in data:
                    data[loc] = 0
                data[loc] += 1
        return data

    def tally_directory_data(self, base_dir):
        """
        Tally the number of files per directory

        :param base_dir: Starting point for tallying

        :return: Dictionary: key=directory, value=count

        """
        tally = {}
        self._build_dict_path(paths=[], data_dict=tally, count=0)

        directories = self.get_image_directories()
        total_images = 0
        for directory in sorted(directories):
            directory.replace(base_dir, '')
            parts = directory.split(os.path.sep)
            tally = self._build_dict_path(paths=parts, data_dict=tally, count=directories[directory])
            total_images += directories[directory]

        LOG.debug(f"Total Images: {total_images}")
        return tally

    @staticmethod
    def _build_dict_path(paths: List[str], data_dict: Dict[str, int],
                         count: int, root: str = os.path.sep) -> Dict[str, int]:
        """
        Builds a nested dictionary where each level is a directory/subdirectory level
        :param paths: Paths to check
        :param data_dict: Dictionary containing root directory and count
        :param count: Number of entries in the current dir (pre-counted)
        :param root: Root or base directory

        :return: Nested dictionary (each level = level of subdirectory, value = count per dir)

        """
        count_key = 'count'
        if root not in data_dict:
            data_dict[root] = {}

        current_loc = data_dict[root]
        for path in paths:

            if path not in current_loc:
                current_loc[path] = {}
            current_loc = current_loc[path]

        if count_key not in current_loc:
            current_loc[count_key] = 0
        current_loc[count_key] = count

        return data_dict

    def directory_stats_table(self, base_dir: str) -> None:
        """
        Build table using directory statistics

        :param base_dir: Base directory (start table at common place/dir)

        :return: None

        """
        tally = self.tally_directory_data(base_dir=base_dir)

        table = prettytable.PrettyTable()
        table.field_names = ['Directory', 'Count']

        for results in tally.values():
            while isinstance(results, dict):
                pass  # Still in progress


class DiskStats:
    """ Build stats based on disk contents """
    FILE_EXT = 'jpg'

    def __init__(self, app_cfg: PdlConfig, file_extension: str = None) -> None:
        self.cfg = app_cfg
        self.extension = file_extension or self.FILE_EXT

    def log_number_in_temp_storage_to_catalog(self, file_extension: str = None) -> None:
        """
        Determine the number of files in the local temp storage
        :param file_extension: Count files of this type

        :return: None

        """
        file_extension = file_extension or self.FILE_EXT

        # Get the number of files (with specified extension)
        dl_inventory_count = num_file_of_type(
            directory=self.cfg.dl_dir, file_type=file_extension)

        LOG.info(f"Number of files in {self.cfg.dl_dir}: {dl_inventory_count}")
