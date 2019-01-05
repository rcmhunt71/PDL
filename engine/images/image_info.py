from pprint import pformat

from PDL.engine.images.status import (
    DownloadStatus as Status,
    ImageDataModificationStatus as ModStatus
)
from PDL.logger.logger import Logger

log = Logger()


class ImageData(object):
    """ Image Metadata Storage Object """

    # Used for checking specific attributes that would not change for the image.
    DL_STATUS = "dl_status"
    IMAGE_NAME = "image_name"
    PAGE_URL = 'page_url'
    IMAGE_URL = 'image_url'
    AUTHOR = 'author'
    DESCRIPTION = 'description'
    RESOLUTION = 'resolution'

    # List of the metadata specific to the image
    METADATA = [DL_STATUS, IMAGE_NAME, PAGE_URL, IMAGE_URL, AUTHOR, DESCRIPTION, RESOLUTION]

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
        self.download_duration = 0
        self.locations = list()
        self.dl_status = Status.NOT_SET
        self.mod_status = ModStatus.MOD_NOT_SET
        self.error_info = None

    def __str__(self):
        return pformat(self.to_dict())

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """
        Convert the object to a dictionary representation.

        :return: dictionary representation of the object.

        """
        attributes = self._list_attributes()
        attr_dict = dict([(key, getattr(self, key)) for key in attributes])
        return attr_dict

    def _list_attributes(self):
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
    def build_obj(cls, dictionary):
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
