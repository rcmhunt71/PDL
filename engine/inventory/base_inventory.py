"""

    Base class for maintaining an inventory. The inventory could be
    file(s), database, etc.

"""
from typing import NoReturn

import PDL.engine.images.image_info as image_info


class BaseInventory:
    """

    This class defines the required/public APIs, and each derived
    inventory management class must implement these classes.

    """
    def __init__(self) -> None:
        self._inventory = dict()

    def get_inventory(self, **kwargs) -> NoReturn:
        """
        Return the contents stored in the class

        :return: TBD

        """
        raise NotImplementedError

    def add_to_inventory(self, element: image_info.ImageData) -> NoReturn:
        """
        Add an element to the inventory

        :param element: ImageData object to be added (WARNING: prototyped too specifically,
             based on module/class description)

        :return: TBD

        """
        raise NotImplementedError

    def remove_from_inventory(self, element_id: str) -> NoReturn:
        """
        Remove element from the inventory

        :param element_id: Id of element to remove

        :return: TBD

        """
        raise NotImplementedError

    def list_inventory(self) -> NoReturn:
        """
        Display inventory (e.g. iterate str(elem))

        :return: TBD

        """
        raise NotImplementedError
