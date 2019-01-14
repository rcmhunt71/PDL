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

        self.fs_inventory = FSInv(
            base_dir=cfg.temp_storage_path, metadata=self.metadata, serialization=True,
            binary_filename=cfg.inv_pickle_file)

        self.fs_inv = self.fs_inventory.get_inventory(
            from_file=True, serialize=True, scan_local=True)

        self.json_inventory = JsonInventory(dir_location=cfg.json_log_location)
        self.json_inv = self.json_inventory.get_inventory()
        # self.complete_inventory = self._accumulate_inv()
        self.complete_inventory = self.json_inv

    def _accumulate_inv(self):
        inv = self.fs_inv
        for image_obj in self.json_inv.keys():
            if image_obj.image_name not in inv.keys():
                log.debug("JSON: Image {0} is new to inventory. Added to inventory.".format(image_obj.image_name))
                inv[image_obj.image_name] = image_obj
                continue

            log.debug("JSON: Image {0} is NOT new to inventory.".format(image_obj.image_name))
            inv[image_obj.image_name] += image_obj

        return inv

    # TODO: Serialize information and write to single, pickled inventory file (for reading later)
    # TODO: Add ability to add/update inventory as needed
