from typing import Dict, List, Optional

from PDL.configuration.properties.app_cfg import AppCfgFileSections, AppCfgFileSectionKeys
from PDL.engine.images.image_info import ImageData
from PDL.engine.inventory.json.inventory import JsonInventory
from PDL.engine.inventory.filesystems.inventory import FSInv
from PDL.logger.logger import Logger

log = Logger()

# TODO: Add docstrings
# TODO: Figure out how to type the __init__ parameters (circular reference)


class Inventory(object):
    def __init__(self, cfg, force_scan=False) -> None:

        self.force_scan = force_scan
        self.metadata = cfg.app_cfg.get_list(
            section=AppCfgFileSections.CLASSIFICATION,
            option=AppCfgFileSectionKeys.TYPES)

        # Get file system inventory
        self.fs_inventory_obj = FSInv(
            base_dir=cfg.temp_storage_path, metadata=self.metadata, serialization=True,
            binary_filename=cfg.inv_pickle_file, force_scan=self.force_scan)
        self.fs_inv = self.fs_inventory_obj.get_inventory(
            from_file=True, serialize=True, scan_local=True)

        # Get JSON listed inventory
        self.json_inventory_obj = JsonInventory(dir_location=cfg.json_log_location)
        self.json_inv = self.json_inventory_obj.get_inventory()

        log.info(f"NUM of FileSystem Records in inventory: {len(self.fs_inv.keys())}")
        log.info(f"NUM of JSON Records in inventory: {len(self.json_inv.keys())}")
        log.info(f"Force Inventory Scan: {self.force_scan}")

        self.inventory = self._accumulate_inv()
        self._pickle_()

    def _accumulate_inv(self) -> Dict[str, ImageData]:
        if self.force_scan:
            total_env = self.fs_inv.copy()
            log.info("Accumulating inventory from file system and JSON logs")

            for image_name, image_obj in self.json_inv.items():
                if image_name not in total_env.keys():
                    log.debug(f"JSON: Image {image_obj.image_name} is new to inventory. Added to inventory.")
                    total_env[image_name] = image_obj
                    continue

                log.debug("JSON: Image {0} is NOT new to inventory.".format(image_obj.image_name))
                total_env[image_name] = total_env[image_name].combine(image_obj)
            total_env = self._make_inv_consistent(data_dict=total_env)
        else:
            log.info(f"Reading from {self.fs_inventory_obj.pickle_fname}")
            total_env = self._unpickle()
            log.info(f"Total of {len(total_env.keys())} read from file.")

        log.info("Accumulation complete.")
        return total_env

    def _pickle_(self, data: Optional[Dict[str, ImageData]] = None) -> None:
        if data is None:
            data = self.inventory
        self.fs_inventory_obj.pickle(data=data, filename=self.fs_inventory_obj.pickle_fname)

    def _unpickle(self) -> Dict[str, ImageData]:
        return self.fs_inventory_obj.unpickle(filename=self.fs_inventory_obj.pickle_fname)

    def get_list_of_page_urls(self) -> List[str]:
        return self._list_of_attribute_values(attr='page_url')

    def get_list_of_image_urls(self) -> List[str]:
        return self._list_of_attribute_values(attr='image_url')

    def get_list_of_images(self) -> List[str]:
        return [x for x in self.inventory.keys()]

    def _list_of_attribute_values(self, attr: str) -> list:
        log.debug("Generating list of '{attr}'s from inventory.".format(attr=attr))
        return [getattr(x, attr) for x in self.inventory.items()
                if hasattr(x, attr) and getattr(x, attr) is not None]

    def update_inventory(self, list_image_data_objs: List[ImageData]) -> None:
        for image_obj in list_image_data_objs:
            image_name = image_obj.image_name
            if image_name in self.inventory.keys():
                log.debug(f"Updating data for {image_name}")
                self.inventory[image_name].combine(image_obj)
            else:
                log.debug(f"Adding data for {image_name}")
                self.inventory[image_name] = image_obj

    @staticmethod
    def _make_inv_consistent(data_dict: Dict[str, ImageData]) -> Dict[str, ImageData]:
        log.info("Making inventory consistent...")
        new_inv = dict()
        for image_name, image_obj in data_dict.items():
            image_name = image_name.split('.')[0].lower()
            if image_name in new_inv.keys():
                new_inv[image_name].combine(image_obj)
            else:
                new_inv[image_name] = image_obj
        return new_inv
