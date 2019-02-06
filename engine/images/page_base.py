from typing import NoReturn


class NotImplementedMethod(Exception):
    """
    Needed to implement a "dumb" class so that nose could test DownloadImage
    The 'NotImplemented' exception does not seem to have a __name__ element,
    so nose throws an AttributeError when the exception is raised. By defining
    a specific exception, the __name__ attribute is present. Go figure.
    """

    msg = "Method: {0} not implemented."

    def __init__(self, routine: str) -> None:
        self.message = self.msg.format(routine)


class ParsePage(object):
    """ Generic object for tracking page parsing actions. """

    def __init__(self, page_url: str) -> None:
        """
        Instantiates new ParsePage object

        :param page_url: URL of page to parse for sub-pages.
        """
        self.page_url = page_url
        self.page_contents = None
        self.image_pages = list()

    def get_image_info(self) -> NoReturn:
        """
        Find and store source page and image metadata.

        :return: None.

        """
        raise NotImplementedMethod('get_image_info')

    def get_page(self) -> NoReturn:
        """
        Download the page (page_url) and store the html contents.
        Does not process page.

        :return: (bool) Status (Success/Failure/Error)
        """
        raise NotImplementedMethod('get_page')

    def parse_page_for_link(self) -> NoReturn:
        """
        Routine for parsing page for sub-pages.

        :return: List of sub-pages found in the primary page
        """
        raise NotImplementedMethod('parse_page_for_link')


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

    def __init__(self, page_url: str, image_urls: list = None) -> None:
        # Using python2.x super() call.
        super(ImageContactPage, self).__init__(page_url)
        self.image_urls = image_urls or list()
