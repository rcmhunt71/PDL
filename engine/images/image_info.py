from typing import List

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
    DL_METADATA = [CLASSIFICATION, DOWNLOADED_ON, ERROR_INFO]

    DEFAULT_VALUES = [None, Status.NOT_SET, ModStatus.MOD_NOT_SET, list(), 0]
    DEBUG_MSG_ADD = "JSON: Image {name}: Added Attribute: '{attr}' Value: '{val}'"

    # TODO: Add support for ImaageData.id in logic throughout app

    def __init__(self):
        self.author = None
        self.classification_metadata = list()
        self.description = None
        self.dl_status = Status.NOT_SET
        self.download_duration = 0
        self.downloaded_on = None
        self.error_info = None
        self.filename = None
        self.file_size = None
        self.id = None
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
        # Iterate through all identified metadata attributes.
        for attribute in ImageData.METADATA + ImageData.DL_METADATA:

            # If the base object ('this') has a default value, and the compared object
            # ('other') has a set value, copy the set value into the base object.
            if (getattr(self, attribute) in self.DEFAULT_VALUES and
                    getattr(self, attribute, None) != getattr(other, attribute, None)):

                setattr(self, attribute, getattr(other, attribute, None))

                # Log the update (debug only)
                log.debug(self.DEBUG_MSG_ADD.format(
                    name=self.image_name, attr=attribute, val=getattr(other, attribute, None)))

        return self

    def combine(self, other: "ImageData") -> "ImageData":
        """
        Combine two objects into a single, new object
        :param other: Populated, instantiated ImageObj

        :return: New ImageData object

        """
        # Create a new object that will be a combination of both self/other.
        new_obj = self.build_obj(self.to_dict())

        # Iterate through the metadata
        for attribute in ImageData.METADATA + ImageData.DL_METADATA:
            this_value = getattr(new_obj, attribute, None)
            other_value = getattr(other, attribute, None)

            # If 'this' has a default value, and the 'other' does not, copy 'other' into 'this'
            if this_value in self.DEFAULT_VALUES and other_value != this_value:
                setattr(new_obj, attribute, other_value)
                log.debug(self.DEBUG_MSG_ADD.format(
                    name=new_obj.image_name, attr=attribute, val=other_value))

        # TODO: Locations should be re-evaluated during scan, and not inherited from ancestors

        return new_obj

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

        return obj
