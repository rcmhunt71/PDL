"""

    Module for defining how to combine inventories of different types
    (into a common data store format)

"""

from typing import Dict, List, Optional

from PDL.configuration.properties.app_cfg import AppCfgFileSections, AppCfgFileSectionKeys
from PDL.engine.images.image_info import ImageData
from PDL.engine.inventory.json.inventory import JsonInventory
from PDL.engine.inventory.filesystems.inventory import FSInv
from PDL.logger.logger import Logger

LOG = Logger()

# TODO: Figure out how to type the __init__ parameters (circular reference)


class Inventory:
    """
    A container class that combines the inventory from multiple sources, such as the
    file system and JSON logs.

    There are routines to combine, enforce consistency, and report that state of the inventory.
    Currently this is done in a pickled, binary file, but can (and should be) replaced
    with a database such as ElasticSearch.
    """
    def __init__(self, cfg, force_scan=False) -> None:
        """
        :param cfg: Instantiated PdlConfig object
        :param force_scan: Bool: Force an inventory scan by default.

        Return: None

        """

        self.force_scan = force_scan

        # Get the classification metadata from the config file
        self.metadata = cfg.app_cfg.get_list(
            section=AppCfgFileSections.CLASSIFICATION,
            option=AppCfgFileSectionKeys.TYPES)

        # Get file system inventory (read from file, unless forced to scan)
        self.fs_inventory_obj = FSInv(
            base_dir=cfg.temp_storage_path, metadata=self.metadata, serialization=True,
            binary_filename=cfg.inv_pickle_file, force_scan=self.force_scan)
        self.fs_inv = self.fs_inventory_obj.get_inventory(
            from_file=True, serialize=True, scan_local=True)

        # Get JSON listed inventory (read from the JSON inv files)
        self.json_inventory_obj = JsonInventory(dir_location=cfg.json_log_location)
        self.json_inv = self.json_inventory_obj.get_inventory()

        LOG.info(f"NUM of FileSystem Records in inventory: {len(self.fs_inv.keys())}")
        LOG.info(f"NUM of JSON Records in inventory: {len(self.json_inv.keys())}")
        LOG.info(f"Force Inventory Scan: {self.force_scan}")

        # Combine the File System and JSON inventory files.
        self.inventory = self._accumulate_inv()

        # Write the updated inventory to file.
        self.write()

    def _accumulate_inv(self) -> Dict[str, ImageData]:
        """
        Combine the various inventory sources (e.g. JSON and File System inventories)
        into a single inventory.

        :return: A dictionary of the combine inventory

        """
        if self.force_scan:

            # Copy the file system inventory as the base inventory (least likely to change)
            total_env = self.fs_inv.copy()
            LOG.info("Accumulating inventory from file system and JSON logs")

            # Add the JSON inventory to the total inventory.
            for image_name, image_obj in self.json_inv.items():

                # If the image is not in the inventory, copy it directly into the inventory.
                if image_name not in total_env.keys():
                    LOG.debug(f"JSON: Image {image_obj.image_name} is new to inventory. "
                              f"Added to inventory.")
                    total_env[image_name] = image_obj
                    continue

                # Image already in inventory. Update the record with info
                # contained in the JSON record.
                LOG.debug("JSON: Image {0} is NOT new to inventory.".format(image_obj.image_name))
                total_env[image_name] = total_env[image_name].combine(image_obj)

            # Due to an older issue, the filename schema may be different for the same image.
            # Verify all images have the same naming nomenclature, and combine records that
            # represent the same file.
            total_env = self._make_inv_consistent(data_dict=total_env)

        # Read the inventory from the pickled inventory file.
        else:
            LOG.info(f"Reading from {self.fs_inventory_obj.pickle_fname}")
            total_env = self._unpickle_()
            LOG.info(f"Total of {len(total_env.keys())} read from file.")

        LOG.info("Accumulation complete.")
        return total_env

    def write(self):
        """
        Write current inventory to file. (Common public interface, hiding _pickle_)
        :return: None

        """
        self._pickle_()

    def _pickle_(self, data: Optional[Dict[str, ImageData]] = None) -> None:
        """
        Write the inventory to file (binary, pickled file)

        :param data: Inventory dictionary (k: image_name, v: ImageData object)

        :return: None

        """
        if data is None:
            data = self.inventory

        self.fs_inventory_obj.pickle(data=data, filename=self.fs_inventory_obj.pickle_fname)

    def _unpickle_(self) -> Dict[str, ImageData]:
        """
        Read the inventory from a pickled/binary file.

        :return: Dictionary for the inventory (k: image_name, v: ImageData object)

        """
        return self.fs_inventory_obj.unpickle(filename=self.fs_inventory_obj.pickle_fname)

    def get_list_of_page_urls(self) -> List[str]:
        """
        Iterate through the inventory, and return the page_urls (source page)

        :return: list of page_urls

        """
        return self._list_of_attribute_values(attr='page_url', allow_none=False)

    def get_list_of_image_urls(self) -> List[str]:
        """
        Iterate through the inventory, and return the image_urls (direct links to the images)

        :return: list of page_urls

        """
        return self._list_of_attribute_values(attr='image_url', allow_none=False)

    def get_list_of_images(self) -> List[str]:
        """
        Return a list of all image names in the inventory.

        :return: List of image names

        """
        return [x for x in self.inventory.keys()]

    def _list_of_attribute_values(self, attr: str, allow_none: bool = False) -> list:
        """
        Generic routine to accumulate the non-None values in the specified attribute.

        :param attr: Object Attribute to accumulate
        :param allow_none: Bool - Allow None as an accepted attribute value.
            Default = False

        :return: List of non-None values stored in all object.<attribute>

        """
        LOG.debug("Generating list of '{attr}'s from inventory.".format(attr=attr))
        return [getattr(x, attr) for x in self.inventory.items()
                if hasattr(x, attr) and getattr(x, attr) is not None or allow_none]

    def update_inventory(self, list_image_data_objs: List[ImageData]) -> None:
        """
        Update total inventory with additional ImageObjs

        :param list_image_data_objs: List of ImageObjs to add to total inventory
        (or use to update existing inventory)

        :return: None

        """
        for image_obj in list_image_data_objs:
            image_name = image_obj.image_name
            if image_name in self.inventory.keys():
                LOG.debug(f"Updating data for {image_name}")
                self.inventory[image_name].combine(image_obj)
            else:
                LOG.debug(f"Adding data for {image_name}")
                self.inventory[image_name] = image_obj

    @staticmethod
    def _make_inv_consistent(data_dict: Dict[str, ImageData]) -> Dict[str, ImageData]:
        """
        Due to an issue where different inventory systems were inconsistent in
        creating the dictionary keys, go through the dictionary:
         * find the inconsistent keys
         * create corresponding "consistent" key
         * check if key is in dictionary
           * Yes: Combine the current record (oupdated key) with the record with the correct key.
           * No: Add key and ImageData object to dictionary

        :param data_dict: Updated inventory (k: image_name, v: ImageData object)

        :return: dict: Updated inventory, with corrected keys.

        """
        LOG.info("Making inventory consistent...")
        new_inv = dict()

        # Iterate through the existing inventory:
        for image_name, image_obj in data_dict.items():

            # Split the keyname. Correct keys will not split, so [0] is the only element.
            # If it is incorrect, the [0] element will be the correct portion of the key to use.
            image_name = image_name.split('.')[0].lower()

            # If the image key exists, combine the corrected with the existing ImageData object
            if image_name in new_inv.keys():
                new_inv[image_name].combine(image_obj)

            # Otherwise, add the ImageData object with the corrected key.
            else:
                new_inv[image_name] = image_obj

        # Return the corrected inventory dictionary
        return new_inv
