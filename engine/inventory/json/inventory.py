import json
import os

from PDL.engine.inventory.base_inventory import BaseInventory
from PDL.logger.logger import Logger
from PDL.engine.images.status import DownloadStatus
from PDL.engine.images.image_info import ImageData

log = Logger()


class JsonInventory(BaseInventory):
    """
    Reads JSON files from a specified directory, converts the JSON to ImageData objects,
       removes duplicates, fills in missing metadata where possible, and
       returns a dictionary of image info:

       key = image_name
       value = ImageData object

     NOTE: Temp solution until database is in place; this solution will not scale well
     for large numbers of JSON files - major performance hit!)

    """
    EXT = "json"

    def __init__(self, dir_location):
        super(JsonInventory, self).__init__()
        self.location = dir_location

    def get_inventory(self):
        """
        Get the unique inventory contained in the JSON files.

        :return: dictionary of image_name: ImageData objects
        """

        # Get list of JSON files
        filename_list = self._get_json_files(loc=self.location)

        # Read all json files and return list of json blobs (1 blob per file)
        content_list = self._read_content(files=filename_list)

        # Parse list of json blobs, update data based on detected duplicates, and
        # build dictionary of ImageData objects.
        inv = self._build_inventory_dict(content_list)
        return inv

    def _get_json_files(self, loc):
        """
        Get list of JSON files (<filespec>.json)

        :param loc: directory containing JSON files

        :return: list of files (with full filespec)

        """
        files = list()
        if os.path.exists(loc):
            files = [os.path.sep.join([loc, x]) for x in os.listdir(loc) if x.lower().endswith(self.EXT.lower())]
        else:
            log.error("Specified directory DOES NOT EXIST: '{0}'".format(loc))
        return files

    def _build_inventory_dict(self, content_list):
        """
        Build the inventory dictionary from the contents of the JSON files.

        Iterates through the content, creates ImageData objects per image, and stores in dictionary:
          key = image_name
          value = ImageData object

        Checks for duplicates, and will save the duplicates. When the checking is complete, check image metadata
        from dups, and if DL'd image's ImageData attribute info is not populate, populate from Dup ImageData [1].

        [1] - This is done because there will be DUPs that were DL'd before this functionality was available.

        :param content_list: List of JSON blobs (1 blob per file)
        :return: Dictionary of Images in inventory (key=image_name, value=ImageData of image)

        """
        inv = dict()
        dups = dict()
        for images_info in content_list:
            for image_name, image_info in images_info.items():
                image_obj = ImageData.build_obj(image_info)

                # If the image name is not in the inventory...
                if image_name not in inv.keys():

                    # If the image was DL'd
                    if image_info[ImageData.DL_STATUS] == DownloadStatus.DOWNLOADED:
                        inv[image_name] = image_obj

                    # Otherwise it may have already existed and included in the JSON, so classify as a DUP.
                    else:
                        self._add_to_dups(dups, image_obj)
                        log.debug("Download Status for '{0}': {1}".format(image_obj.image_name, image_obj.dl_status))
                        log.debug("Duplicate in the inventory? {0}".format(image_obj.image_name in inv))

                # Image was already in the inventory.
                else:
                    self._add_to_dups(dups, image_obj)
                    log.debug("Download Status for '{0}': {1}".format(image_obj.image_name, image_obj.dl_status))
                    log.debug("Duplicate in the inventory? {0}".format(image_obj.image_name in inv))

        # Update the metadata of the inventory, if needed, and return the inventory dict.
        return self._update_info(inv, dups)

    @staticmethod
    def _update_info(inv_dict, dups_dict):
        """
        For images that were DL'd and recorded in the JSON, check if the image metadata is not in the original
        inventory, and update object (although it is not recorded).

        :param inv_dict: Inventory dictionary. key = image_name, value = ImageData obj

        :param dups_dict: Duplicate dictionary. key = image_name, value = list of ImageData objs

        :return: updated Inventory dictionary
        """
        attributes_list = ImageData.METADATA
        for dup_name, dup_image_info_list in dups_dict.items():
            for dup_image_obj in dup_image_info_list:
                for attribute in attributes_list:
                    if (dup_name in inv_dict and
                            getattr(inv_dict[dup_name], attribute) is None and
                            getattr(dup_image_obj, attribute) is not None):
                        setattr(inv_dict[dup_name], attribute, getattr(dup_image_obj, attribute))
                        log.debug("Updating original image info for {image}: Attr: '{attrib}' : '{value}'".format(
                            attrib=attribute, value=getattr(inv_dict[dup_name], attribute), image=dup_name))
        return inv_dict

    @staticmethod
    def _add_to_dups(dictionary, image_data_obj):
        """
        Convenience function for adding an ImagaData object to the duplicates dictionary

        :param dictionary: Duplicates dictionary
        :param image_data_obj: ImageData object to be added.

        :return: duplicates dictionary

        """
        image_name = image_data_obj.image_name
        log.debug("Duplicate found: {0}".format(image_name))

        if image_name not in dictionary:
            dictionary[image_name] = list()
        dictionary[image_name].append(image_data_obj)

        return dictionary

    @staticmethod
    def _read_content(files):
        """
        Read json file and append contents to a storage list

        :param files: List of files to read (full path filespec required)

        :return: List of JSON blobs, 1 blob per file.

        """
        content = list()
        for json_file in files:
            with open(json_file) as FILE:
                lines = FILE.readlines()
            content.append(json.loads(''.join(lines)))
        return content
