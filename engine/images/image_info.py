import os
from typing import List, Optional

from PDL.engine.images.status import (
    DownloadStatus as Status,
    ImageDataModificationStatus as ModStatus
)
from PDL.logger.logger import Logger

import prettytable

log = Logger()


"""
Provides a basic structure for storing metadata and location data about a single
downloaded image. NOTE This class is simple, and should remain simple, since it
is only for data storage.

The class also has some simple helper methods for reporting/displaying the information.

"""


class ImageData(object):

    # Metadata used for checking specific attributes that would not change for the image. The
    # values of these variables should match the defined class attributes.

    AUTHOR = 'author'
    CLASSIFICATION = 'classification_metadata'
    DESCRIPTION = 'description'
    DL_STATUS = "dl_status"
    DOWNLOADED_ON = 'downloaded_on'
    ERROR_INFO = 'error_info'
    FILENAME = 'filename'
    FILE_SIZE = 'file_size'
    ID = 'id'
    IMAGE_NAME = "image_name"
    LOCATIONS = 'locations'
    PAGE_URL = 'page_url'
    RESOLUTION = 'resolution'
    IMAGE_URL = 'image_url'
    IMAGE_DATE = 'image_date'

    # List of the metadata specific to the image (in order of importance/relation
    # but many reports will reorder alphabetically.
    METADATA = [DL_STATUS, IMAGE_NAME, PAGE_URL, IMAGE_URL,
                AUTHOR, DESCRIPTION, RESOLUTION, FILENAME,
                FILE_SIZE, IMAGE_DATE, ID]
    DL_METADATA = [CLASSIFICATION, DOWNLOADED_ON, ERROR_INFO, LOCATIONS]

    DEFAULT_VALUES = [None, Status.NOT_SET, ModStatus.MOD_NOT_SET, list(), 0]
    DEBUG_MSG_ADD = "JSON: Image {name}: Added Attribute: '{attr}' Value: '{val}'"

    def __init__(self, image_id=None):
        self.author = None
        self.classification_metadata = list()
        self.description = None
        self.dl_status = Status.NOT_SET
        self.download_duration = 0
        self.downloaded_on = None
        self.error_info = None
        self.filename = None
        self.file_size = None
        self.id = image_id
        self.image_date = None
        self.image_name = None
        self.image_url = None
        self.locations = list()
        self.mod_status = ModStatus.MOD_NOT_SET
        self.page_url = None
        self.resolution = None

    def __str__(self) -> str:
        return f"\n{self.table()}"

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, other: "ImageData") -> "ImageData":
        return self.combine(other, use_self=True)

    @staticmethod
    def _verify_locations(obj: "ImageData") -> List[str]:
        """
        Given a list of locations for the image, verify the image exists in those locations.
        Save the locations to a new list where the image exists,
        otherwise disregard the missing locations.

        :param obj: ImageData obj with locations list

        :return: List of validation locations for the image

        """
        locations = list()

        # For each location stored in ImageData.locations
        for loc in obj.locations:

            # Determine the full path
            full_path = os.path.abspath(os.path.sep.join([loc, obj.filename]))

            action = 'NOT FOUND'
            sub_action = ''

            # Check if the image exists...
            if os.path.exists(full_path):
                locations.append(loc)
                action = 'found'
                sub_action = "--> Adding to location list."

            # Log the result accordingly
            log.debug(f'{obj.id} was {action} in location: {loc} {sub_action}')

        return locations

    def combine(self, other: "ImageData", use_self: bool = False) -> "ImageData":
        """
        Combine two objects into a single, new object
        :param other: Populated, instantiated ImageObj to combine to self
        :param use_self: If True, use 'self' object, otherwise create and return a new object.

        :return: New ImageData object

        """
        # Create a new object that will be a combination of both self/other.
        combined_obj = self
        if not use_self:
            combined_obj = self.build_obj(self.to_dict())

        # Iterate through the metadata
        for attribute in ImageData.METADATA + ImageData.DL_METADATA:
            this_value = getattr(combined_obj, attribute, None)
            other_value = getattr(other, attribute, None)

            # If 'this' has a default value, and the 'other' does not, copy 'other' into 'this'
            if this_value in self.DEFAULT_VALUES and other_value != this_value:
                setattr(combined_obj, attribute, other_value)
                log.debug(self.DEBUG_MSG_ADD.format(
                    name=combined_obj.image_name, attr=attribute, val=other_value))

            # For locations, combine the lists and then verify
            elif attribute == ImageData.LOCATIONS:
                combined_obj.locations.extend(other.locations)
                combined_obj.locations = list(set(combined_obj.locations))
                combined_obj.locations = self._verify_locations(obj=combined_obj)

        return combined_obj

    def table(self) -> str:
        """
        Generate a stringified table representation of the object

        :return: str - table

        """
        attribute = 'Attribute'
        value = 'Value'

        # Define the table
        table = prettytable.PrettyTable()
        table.field_names = [attribute, value]
        table.align[attribute] = 'l'
        table.align[value] = 'l'

        # Populate the table
        for attrib in sorted(self._list_attributes()):
            table.add_row([attrib, getattr(self, attrib)])

        # Return the table
        return table.get_string(title=self.image_name)

    def to_dict(self) -> dict:
        """
        Convert the object to a dictionary representation.

        :return: dictionary representation of the object.

        """
        attributes = self._list_attributes()
        attr_dict = dict([(key, getattr(self, key)) for key in attributes])
        return attr_dict

    def _list_attributes(self) -> List[str]:
        """
        List of all object attributes:
          * not callable,
          * no capital letters (PEP-8)
          * does not start with '_' ==> internal attributes

        :return: list of all object attributes

        """
        return [x for x in dir(self) if not x.startswith('_')
                and x.lower() == x and not callable(getattr(self, x))]

    @classmethod
    def build_obj(cls, dictionary: dict) -> "ImageData":
        """
        Builds an object from a dictionary implementation
        :param dictionary: Dictionary representation of the ImageData object

        :return: Instantiated, populated ImageData object

        """
        attr_err_msg = "Unrecognized ImageData attribute: '{attr}' , value: {val}"

        obj = ImageData()

        # Iterate through the provided data, and if the attribute exists in the class definition,
        # populate the object attribute
        for key, value in dictionary.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

            # Found a key that is not in the class attribution definition
            else:
                log.error(attr_err_msg.format(attr=key, val=value))

        # If obj being built is legacy and does not have an ID defined, set the ID.
        if hasattr(obj, cls.FILENAME) and getattr(obj, cls.ID) is None:
            setattr(obj, cls.ID, cls.FILENAME.split(".")[0])

        return obj
