from PDL.configuration.properties.app_cfg import AppCfgFileSections, AppCfgFileSectionKeys
from PDL.engine.inventory.json.inventory import JsonInventory
from PDL.engine.inventory.filesystems.inventory import FSInv
from PDL.logger.logger import Logger

log = Logger()


class Inventory(object):
    def __init__(self, cfg, force_scan=False):

        self.metadata = cfg.app_cfg.get_list(
            section=AppCfgFileSections.CLASSIFICATION,
            option=AppCfgFileSectionKeys.TYPES)

        # Get file system inventory
        self.fs_inventory_obj = FSInv(
            base_dir=cfg.temp_storage_path, metadata=self.metadata, serialization=True,
            binary_filename=cfg.inv_pickle_file, scan=force_scan)
        self.fs_inv = self.fs_inventory_obj.get_inventory(
            from_file=True, serialize=True, scan_local=True)

        # Get JSON listed inventory
        self.json_inventory_obj = JsonInventory(dir_location=cfg.json_log_location)
        self.json_inv = self.json_inventory_obj.get_inventory()

        log.info("NUM of FileSystem Records in inventory: {0}".format(len(self.fs_inv.keys())))
        log.info("NUM of JSON Records in inventory: {0}".format(len(self.json_inv.keys())))

        self.inventory = self._accumulate_inv()
        self._pickle_()

    def _accumulate_inv(self):
        total_env = self.fs_inv.copy()
        for image_name, image_obj in self.json_inv.items():
            if image_name not in total_env.keys():
                log.debug("JSON: Image {0} is new to inventory. Added to inventory.".format(image_obj.image_name))
                total_env[image_name] = image_obj
                continue

            log.debug("JSON: Image {0} is NOT new to inventory.".format(image_obj.image_name))
            total_env[image_name] = total_env[image_name].combine(image_obj)

        return total_env

    def _pickle_(self):
        self.fs_inventory_obj.pickle(data=self.inventory,
                                     filename=self.fs_inventory_obj.pickle_fname)

    def _unpickle(self):
        return self.fs_inventory_obj.unpickle(filename=self.fs_inventory_obj.pickle_fname)

    def get_list_of_page_urls(self):
        return self._list_of_attribute_values(attr='page_url')

    def get_list_of_image_urls(self):
        return self._list_of_attribute_values(attr='image_url')

    def get_list_of_images(self):
        return self.inventory.keys()

    def _list_of_attribute_values(self, attr):
        log.debug("Generating list of '{attr}'s from inventory.".format(attr=attr))
        return [getattr(x, attr) for x in self.inventory.items()
                if hasattr(x, attr) and getattr(x, attr) is not None]

    def update_inventory(self, list_image_data_objs):
        for image_obj in list_image_data_objs:
            image_name = image_obj.image_name
            if image_name in self.inventory.keys():
                log.debug("Updating data for {0}".format(image_name))
                self.inventory[image_name].combine(image_obj)
            else:
                log.debug("Adding data for {0}".format(image_name))
                self.inventory[image_name] = image_obj
