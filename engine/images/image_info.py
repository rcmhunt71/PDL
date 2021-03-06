"""

    Image Metadata Tracking Class

"""

import os
from dataclasses import dataclass, field
from typing import List

import prettytable

from PDL.engine.images.status import (
    DownloadStatus as Status,
    ImageDataModificationStatus as ModStatus
)
from PDL.logger.logger import Logger


LOG = Logger()


@dataclass
class ImageData:
    """
    Provides a basic structure for storing metadata and location data about a single
    downloaded image. NOTE This class is simple, and should remain simple, since it
    is only for data storage.

    The class also has some simple helper methods for reporting/displaying the information.

    """

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
    ID = 'id_'
    IMAGE_NAME = "image_name"
    LOCATIONS = 'locations'
    PAGE_URL = 'page_url'
    RESOLUTION = 'resolution'
    IMAGE_URL = 'image_url'
    IMAGE_DATE = 'image_date'
    EXTENSION = 'jpg'

    # List of the metadata specific to the image (in order of importance/relation
    # but many reports will reorder alphabetically.
    METADATA = [DL_STATUS, IMAGE_NAME, PAGE_URL, IMAGE_URL,
                AUTHOR, DESCRIPTION, RESOLUTION, FILENAME,
                FILE_SIZE, IMAGE_DATE, ID]
    DL_METADATA = [CLASSIFICATION, DOWNLOADED_ON, ERROR_INFO, LOCATIONS]

    DEFAULT_VALUES = [None, Status.NOT_SET, ModStatus.MOD_NOT_SET, [], 0.0, 0]
    DEBUG_MSG_ADD = "JSON: Image {name}: Added Attribute: '{attr}' Value: '{val}'"

    author: str = field(default=None, metadata={'descr': 'Photographer'})
    classification_metadata: List[str] = field(
        default_factory=lambda: [], metadata={'descr': 'Classifications'})
    description: str = field(default=None, metadata={'descr': 'Description of image'})
    dl_status: str = field(default=Status.NOT_SET, metadata={'descr': 'Download Status'})
    download_duration: float = field(
        default=0.0, metadata={'descr': 'Time taken to download'})
    downloaded_on: str = field(default=None, metadata={'descr':'Timestamp of download'})
    error_info: str = field(default=None, metadata={'descr': 'Errors encountered during DL'})
    filename: str = field(default=None, metadata={'descr': 'Name of image file'})
    file_size: str = field(default='unknown', metadata={'descr': 'Size of image file, in KB'})
    id_: str = field(default=None, metadata={'descr': 'Unique Identification Str'})
    image_date: str = field(default=None, metadata={'descr': 'Date photo was taken'})
    image_name: str = field(default=None, metadata={'descr': 'Title of Image'})
    image_url: str = field(default=None, metadata={'descr': 'URL of Image DL'})
    locations: List[str] = field(
        default_factory=lambda: [], metadata={'descr': 'List of locations image is stored'})
    mod_status: str = field(
        default=ModStatus.MOD_NOT_SET, metadata={'descr': 'Database Status'})
    page_url: str = field(default=None, metadata={'descr': 'Primary Page URL'})
    resolution: str = field(default=None, metadata={'descr': 'Image Resolution: L x W'})

    def __str__(self) -> str:
        return f"\n{self.table()}"

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, other: "ImageData") -> "ImageData":
        return self.combine(other, use_self=True)

    def _verify_locations(self, obj: "ImageData") -> List[str]:
        """
        Given a list of locations for the image, verify the image exists in those locations.
        Save the locations to a new list where the image exists,
        otherwise disregard the missing locations.

        :param obj: ImageData obj with locations list

        :return: List of validation locations for the image

        """
        locations = list()

        # For each location stored in ImageData.locations
        for loc in set(getattr(obj, ImageData.LOCATIONS)):

            # Determine the full path
            filename = getattr(obj, ImageData.FILENAME)
            if not filename.lower().endswith(self.EXTENSION):
                setattr(obj, ImageData.FILENAME, f"{filename}.{self.EXTENSION}")

            full_path = os.path.abspath(os.path.sep.join(
                [loc, getattr(obj, ImageData.FILENAME)]))

            action = 'NOT FOUND'
            sub_action = ''

            # Check if the image exists...
            if os.path.exists(full_path):
                locations.append(loc)
                action = 'found'
                sub_action = "--> Adding to location list."

            # Log the result accordingly
            LOG.debug(f'{obj.id_} was {action} in location: {loc} {sub_action}')

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

            # For locations, combine the lists and then verify
            if attribute == ImageData.LOCATIONS:

                # Due to setting dataclass, pylint shows error if lists are not cast as lists
                # (listed as a 'field' which does not have an .extend method).
                # Cast as a lists (list -> set -> list), and store as combined_obj.locations()
                # and cast via list(set()) to remove duplicates.
                loc_1 = list(set(getattr(combined_obj, ImageData.LOCATIONS)))
                loc_1.extend(list(set(getattr(other, ImageData.LOCATIONS))))
                setattr(combined_obj, ImageData.LOCATIONS, list(set(loc_1)))

                # Verify all locations are valid
                setattr(combined_obj, ImageData.LOCATIONS,
                        self._verify_locations(obj=combined_obj))

            # If 'this' has a default value, and the 'other' does not, copy 'other' into 'this'
            elif this_value in self.DEFAULT_VALUES and other_value != this_value:
                setattr(combined_obj, attribute, other_value)
                LOG.debug(self.DEBUG_MSG_ADD.format(
                    name=getattr(combined_obj, ImageData.IMAGE_NAME),
                    attr=attribute, val=other_value))

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
        attr_dict = {key: getattr(self, key) for key in attributes}
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
        obj = ImageData()

        # Iterate through the provided data, and if the attribute exists in the class definition,
        # populate the object attribute
        for key, value in dictionary.items():

            # Fix legacy issue where name changed from id to id_
            if key == 'id':
                key = cls.ID
            if hasattr(obj, key):
                setattr(obj, key, value)

            # Found a key that is not in the class attribution definition
            else:
                LOG.error(f"Unrecognized ImageData attribute: '{key}' , value: {value}")

        # If obj being built is legacy and does not have an ID defined, set the ID.
        # Also fix bug where wrong variable was used, so metadata id was set to
        # 'filename' instead of actual id.
        if hasattr(obj, cls.FILENAME) and getattr(obj, cls.FILENAME) is not None:
            if getattr(obj, cls.ID) is None or getattr(obj, cls.ID) == cls.FILENAME:
                setattr(obj, cls.ID, str(getattr(obj, cls.FILENAME)).split(".")[0])

            # TODO: Find where filename is stripping the extension and remove this temp fix (hack)
            if not str(getattr(obj, cls.FILENAME)).lower().endswith(cls.EXTENSION):
                setattr(obj, cls.FILENAME, f"{getattr(obj, cls.FILENAME)}.{cls.EXTENSION}")

        return obj
