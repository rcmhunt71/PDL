from typing import List

from PDL.engine.images.status import (
    DownloadStatus as Status,
    ImageDataModificationStatus as ModStatus
)
from PDL.logger.logger import Logger

import prettytable

log = Logger()


# TODO: Add docstrings


class ImageData(object):
    """ Image Metadata Storage Object """

    # Used for checking specific attributes that would not change for the image.
    AUTHOR = 'author'
    CLASSIFICATION = 'classification_metadata'
    DESCRIPTION = 'description'
    DL_STATUS = "dl_status"
    DOWNLOADED_ON = 'downloaded_on'
    ERROR_INFO = 'error_info'
    FILENAME = 'filename'
    FILE_SIZE = 'file_size'
    IMAGE_NAME = "image_name"
    LOCATIONS = 'locations'
    PAGE_URL = 'page_url'
    IMAGE_URL = 'image_url'
    IMAGE_DATE = 'image_date'
    RESOLUTION = 'resolution'

    # List of the metadata specific to the image
    METADATA = [DL_STATUS, IMAGE_NAME, PAGE_URL, IMAGE_URL, AUTHOR, DESCRIPTION, RESOLUTION, FILENAME,
                IMAGE_DATE, FILE_SIZE]
    DL_METADATA = [CLASSIFICATION, DOWNLOADED_ON, ERROR_INFO]

    DEFAULT_VALUES = [None, Status.NOT_SET, ModStatus.MOD_NOT_SET, list(), 0]
    DEBUG_MSG_ADD = "JSON: Image {name}: Added Attribute: '{attr}' Value: '{val}'"

    def __init__(self):
        self.image_name = None
        self.description = None
        self.page_url = None
        self.image_url = None
        self.author = None
        self.filename = None
        self.image_date = None
        self.resolution = None
        self.downloaded_on = None
        self.classification_metadata = list()
        self.download_duration = 0
        self.locations = list()
        self.dl_status = Status.NOT_SET
        self.mod_status = ModStatus.MOD_NOT_SET
        self.error_info = None
        self.file_size = None

        # TODO: Add self.filesize + calc during DL or Inv.

    def __str__(self) -> str:
        return f"\n{self.table()}"

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, other: "ImageData") -> "ImageData":
        # NOTE: Not a commutative operation, obj application order matters

        for attribute in ImageData.METADATA + ImageData.DL_METADATA:
            if (getattr(self, attribute) in self.DEFAULT_VALUES and
                    getattr(self, attribute, None) != getattr(other, attribute, None)):

                setattr(self, attribute, getattr(other, attribute, None))
                log.debug(self.DEBUG_MSG_ADD.format(
                    name=self.image_name, attr=attribute, val=getattr(other, attribute, None)))
        return self

    def combine(self, other: "ImageData") -> "ImageData":
        new_obj = self.build_obj(self.to_dict())
        for attribute in ImageData.METADATA + ImageData.DL_METADATA:
            this_value = getattr(new_obj, attribute, None)
            other_value = getattr(other, attribute, None)
            if this_value in self.DEFAULT_VALUES and other_value != this_value:
                setattr(new_obj, attribute, other_value)
                log.debug(self.DEBUG_MSG_ADD.format(
                    name=new_obj.image_name, attr=attribute, val=other_value))

        # TODO: Locations should be re-evalauted during scan, and not inherited from ancestors

        return new_obj

    def table(self) -> str:
        attribute = 'Attribute'
        value = 'Value'

        table = prettytable.PrettyTable()
        table.field_names = [attribute, value]
        for attrib in sorted(self._list_attributes()):
            table.add_row([attrib, getattr(self, attrib)])
        table.align[attribute] = 'l'
        table.align[value] = 'l'
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
        for key, value in dictionary.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
            else:
                log.error(attr_err_msg.format(attr=key, val=value))
        return obj
