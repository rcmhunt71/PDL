class ParsePage(object):
    """ Generic object for tracking page parsing actions. """

    def __init__(self, page_url):
        """
        Instantiates new ParsePage object

        :param page_url: URL of page to parse for sub-pages.
        """
        self.page_url = page_url
        self.page_contents = None
        self.image_pages = list()

    def get_page(self):
        """
        Download the page (page_url) and store the html contents.
        Does not process page.

        :return: (bool) Status (Success/Failure/Error)
        """
        raise NotImplemented

    def parse_page(self):
        """
        Routine for parsing page for sub-pages.

        :return: List of sub-pages found in the primary page
        """
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
