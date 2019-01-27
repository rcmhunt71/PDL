from PDL.configuration.properties.app_cfg import AppCfgFileSections, AppCfgFileSectionKeys
from PDL.engine.inventory.json.inventory import JsonInventory
from PDL.engine.inventory.filesystems.inventory import FSInv
from PDL.logger.logger import Logger

log = Logger()


class Inventory(object):
    def __init__(self, cfg):

        self.metadata = cfg.app_cfg.get_list(
            section=AppCfgFileSections.CLASSIFICATION,
            option=AppCfgFileSectionKeys.TYPES)

        # Get file system inventory
        self.fs_inventory_obj = FSInv(
            base_dir=cfg.temp_storage_path, metadata=self.metadata, serialization=True,
            binary_filename=cfg.inv_pickle_file)
        self.fs_inv = self.fs_inventory_obj.get_inventory(
            from_file=True, serialize=True, scan_local=True)

        # Get JSON listed inventory
        self.json_inventory_obj = JsonInventory(dir_location=cfg.json_log_location)
        self.json_inv = self.json_inventory_obj.get_inventory()

        log.info("NUM of FileSystem Records in inventory: {0}".format(len(self.fs_inv.keys())))
        log.info("NUM of JSON Records in inventory: {0}".format(len(self.json_inv.keys())))

        self.complete_inventory = self._accumulate_inv()
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
        self.fs_inventory_obj.pickle(data=self.complete_inventory,
                                     filename=self.fs_inventory_obj.pickle_fname)

    def _unpickle(self):
        return self.fs_inventory_obj.unpickle(filename=self.fs_inventory_obj.pickle_fname)

    # TODO: Add ability to add/update inventory as needed
