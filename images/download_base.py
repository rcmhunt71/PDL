
class ParsePage(object):
    """ Generic object for tracking page parsing actions. """

    # TODO: Add docstring
    def __init__(self, page_url):
        self.page_url = page_url
        self.page_contents = None
        self.image_pages = list()

    def get_page(self):
        raise NotImplemented

    def parse_page(self):
        raise NotImplemented


class CatalogPage(ParsePage):
    """
    Used when a series of contact sheets are listed: catalog of groups of images
    Return list of ImageContactPage objects
    """

    pass


class ImageContactPage(ParsePage):
    """
    Used to determine metadata and URL of image(s) parsed from page.
    Return: List of ImageData objects
    """

    def __init__(self, page_url):
        # Using python2.x super() call.
        super(ImageContactPage, self).__init__(page_url)
        self.image_urls = list()


class ImageStatus(object):
    # TODO: Add docstrings

    def __init__(self, image_list):
        self.image_list = image_list

    def does_image_exist(self):
        raise NotImplemented


class DownloadImages(object):
    # TODO: Add docstrings

    def __init__(self, image_list):
        self.image_list = image_list

    def download_image(self):
        raise NotImplemented
