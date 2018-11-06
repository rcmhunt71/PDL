import re
import requests
import time
from urllib.parse import quote

from PDL.engine.images.image_info import ImageData
from PDL.engine.images.page_base import CatalogPage
from PDL.engine.images.status import DownloadStatus
from PDL.logger.logger import Logger

log = Logger()

# TODO: Write tests
# TODO: Add code documentation explaining approach


class ParseDisplayPage(CatalogPage):

    HEADERS = {
        'user-agent':
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'}

    RETRY_INTERVAL = 5
    MAX_ATTEMPTS = 3
    KEY = 'jpeg'

    def __init__(self, page_url):
        super().__init__(page_url=page_url)
        self.source = self.get_page()
        self.image_info = ImageData()
        self.get_image_info()

    def get_image_info(self):
        """
        Store any collected info into the ImageData object

        :return: None

        """
        self.image_info.page_url = self.page_url
        self.image_info.image_url = self.parse_page_for_link()
        self.image_info.author = self.get_author_name()

    def get_page(self):
        """
        Get url source code

        :return: list of source code (line by line)

        """
        conn_err = ("{{attempt}}/{max}: Connection Error --> Trying again in "
                    "{delay} seconds".format(delay=self.RETRY_INTERVAL,
                                             max=self.MAX_ATTEMPTS))

        attempt = 0
        source = None

        # Attempt to retrieve primary page via requests.GET()
        while attempt <= self.MAX_ATTEMPTS:
            attempt += 1
            log.debug("(attempt: {attempt}: Requesting page: '{url}'".format(
                url=self.page_url, attempt=attempt))

            try:
                source = requests.get(url=self.page_url, headers=self.HEADERS)

            # D'oh!! Connection error...
            except requests.exceptions.ConnectionError:
                log.warn(conn_err.format(attempt=attempt))
                time.sleep(self.RETRY_INTERVAL)

        log.debug("Primary page '{url}' DL'd!".format(url=self.page_url))

        # Split and strip the page into a list (elem per line), based on CR/LF.
        if source is not None:
            source = [x.strip() for x in source.text.split('\n')]

        return source

    def parse_page_for_link(self):
        """
        Retrieve the originating page, and get the desired image link out of
        the page.

        :param source: Raw string od source from html page
        :return: Image URL that was embedded in the original page

        """
        url_regexp = (r'size\"\s*:\s*2048\s*,\s*\"url\"\s*:\s*\"'
                      r'(?P<url>https:.*)\",\"https_url\"')

        # Reduce data to only check lines with the KEY (jpg) is found
        lines = [line for line in self.source if self.KEY in line]
        patt = re.compile(url_regexp)

        # Try to find largest resolution image link (there are multiple links,
        # one for each size)
        for line in lines:
            result = patt.search(line)
            if result is not None:
                link = result.group('url').replace('\/', '/')
                return self.translate_unicode_in_link(link=link)

        # If you get here, you parsed the whole page and found nada...
        log.error('Unable to find url in source page.')
        log.error('SOURCE:\n{source}'.format(source=self.source))
        self.image_info.dl_status = DownloadStatus.ERROR

        return None

    def get_author_name(self):
        """
        Get the author's name, if it is embedded in the page.

        :return: (str) Author's name

        """
        key = 'fullname'
        regexp_pattern = r'"fullname"\:"(?P<author>.*?)","'

        # Find all lines with the 'key' word
        lines = [line for line in self.source if key in line]

        # Check each link for the regexp, which will contain the author's name
        for line in lines:
            result = re.search(pattern=regexp_pattern, string=line)
            if result is not None:
                return result.group('author')

        return 'Not Found'

    @staticmethod
    def translate_unicode_in_link(link):
        """
        Adds quoting around unicode embedded in the links

        :param link: URL to convert/translate

        :return: Translated link

        """
        url_regexp_pattern = r'https://(?P<domain>[\w\d\.]+)/(?P<path>.*)'

        result = re.search(url_regexp_pattern, link)

        if result is not None:
            path = quote(result.group('path'))
            link = 'https://{domain}/{path}'.format(
                domain=result.group('domain'), path=path)

        return link