class BaseInventory(object):
    """
    Base class for maintaining an inventory. The inventory could be
    file(s), database, etc.

    This class defines the required/public APIs, and each derived
    inventory management class must implement these classes.

    """
    def __init__(self):
        self._inventory = dict()

    def get_inventory(self):
        raise NotImplemented

    def add_to_inventory(self, element):
        raise NotImplemented

    def remove_from_inventory(self, element):
        raise NotImplemented

    def list_inventory(self):
        raise NotImplemented
