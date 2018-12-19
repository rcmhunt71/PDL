import datetime
import json
import pprint
import re
import time
import unicodedata

import requests
from PDL.engine.images.image_info import ImageData
from PDL.engine.images.page_base import CatalogPage
from PDL.engine.images.status import DownloadStatus
from PDL.logger.logger import Logger
from six.moves.urllib.parse import quote

log = Logger()

# TODO: <DOC> Add code documentation explaining approach


class ParseDisplayPage(CatalogPage):

    HEADERS = {
        'user-agent':
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'}

    RETRY_INTERVAL = 5
    MAX_ATTEMPTS = 3
    KEY = 'jpeg'
    NOT_FOUND = 'Not Found'
    EXTENSION = 'jpg'

    # SOURCE PAGE CONSTANTS
    CREATED_AT = 'created_at'
    DESCRIPTION = 'description'
    HEIGHT = "height"
    IMAGES = 'images'
    NAME = 'name'
    PHOTO = 'photo'
    SIZE = 'size'
    URL = 'url'
    USER = 'user'
    USERNAME = 'username'
    WIDTH = "width"

    def __init__(self, page_url):
        super(ParseDisplayPage, self).__init__(page_url=page_url)
        self.image_info = ImageData()
        self.source_list = None
        self._metadata = None

    def get_image_info(self):
        """
        Store any collected info into the ImageData object

        :return: None

        """
        if self.source_list is None:
            self.source_list = self.get_page()
            self._metadata = self._get_metadata()

        self.image_info.page_url = self.page_url
        self.image_info.image_url = self.parse_page_for_link()
        self.image_info.author = self._get_author_name()
        self.image_info.image_name = self._get_title()
        self.image_info.description = self._get_description()
        self.image_info.image_date = self._get_image_date()
        self.image_info.resolution = self._get_resolution()
        self.image_info.filename = self._get_filename()

    def _get_author_name(self):
        return self._metadata[self.PHOTO][self.USER][self.USERNAME]

    def _get_title(self):
        return self._metadata[self.PHOTO][self.NAME]

    def _get_description(self):
        return self._metadata[self.PHOTO][self.DESCRIPTION]

    def _get_image_date(self):
        date = datetime.datetime.fromisoformat(self._metadata[self.PHOTO][self.CREATED_AT])
        return str(date.isoformat()).split('.')[0]

    def _get_filename(self):
        filename = (self._get_image_url() if self.image_info.image_url is None
                    else self.image_info.image_url)

        return '{filename}.{ext}'.format(
            filename=filename.split("=")[-1], ext=self.EXTENSION)

    def _get_resolution(self):
        width = self._metadata[self.PHOTO][self.WIDTH]
        height = self._metadata[self.PHOTO][self.HEIGHT]
        return "{width}x{height}".format(width=width, height=height)

    def _get_image_url(self):
        image_list = self._metadata[self.PHOTO][self.IMAGES]
        image_list.sort(key=lambda x: x[self.SIZE])
        target_url = image_list[-1][self.URL]

        log.debug("URL LIST:\n{0}".format(pprint.pformat(image_list)))
        log.debug("Returning URL: {0}".format(target_url))

        return target_url

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
        log_msg = "Attempt: {attempt}/{max}: Requesting page: '{url}'"
        while attempt < self.MAX_ATTEMPTS and source is None:
            attempt += 1
            log.debug(log_msg.format(
                url=self.page_url, attempt=attempt, max=self.MAX_ATTEMPTS))

            try:
                source = requests.get(url=self.page_url, headers=self.HEADERS)

            # D'oh!! Connection error...
            except requests.exceptions.ConnectionError:
                log.warn(conn_err.format(attempt=attempt))
                time.sleep(self.RETRY_INTERVAL)

        if attempt < self.MAX_ATTEMPTS:
            log.info("Primary page '{url}' DL'd!".format(url=self.page_url))

        # Split and strip the page into a list (elem per line), based on CR/LF.
        if source is not None:
            source = [x.strip() for x in source.text.split('\n')]

        return source

    def _get_domain_from_url(self):
        domain_pattern = r'http.://(?P<domain>(\w+\.)?\w+\.\w+)/.*'

        domain = None
        match = re.search(domain_pattern, self.page_url)
        if match is not None:
            domain = match.group('domain')
        log.debug("DOMAIN: {0}".format(domain))
        return domain

    def parse_page_for_link(self):
        """
        Retrieve the originating page, and get the desired image link out of
        the page.

        :return: Image URL that was embedded in the original page

        """

        web_url = 'web'
        www_url = '500px'

        domain = self._get_domain_from_url().lower()
        if domain.startswith(web_url):
            url = self._get_image_url()

        elif domain.startswith(www_url):
            url = self._get_image_url()

        else:
            err_msg = ('Unrecognized domain format: {domain} - '
                       'Unsure how to proceed.')
            log.error(err_msg.format(domain=domain))
            self.image_info.dl_status = DownloadStatus.ERROR
            self.image_info.error_info = err_msg
            url = None

        return url

    def _get_metadata(self):
        metadata = None

        # Get PreLoaded Data, which contains image metadata
        data_pattern = r'window\.PxPreloadedData\s*=\s*(?P<data>.*?);'
        match = re.search(data_pattern, ''.join(self.source_list))

        if match is not None:

            # Remove control characters
            raw_data = self.remove_control_characters(match.group('data'))

            # Adjust brace count to be zero if partial DOM is retrieved
            mismatch = raw_data.count("{") - raw_data.count("}")
            log.debug("Brace mismatch count: {0}".format(mismatch))
            raw_data = "{0}{1}".format(raw_data, '}' * mismatch)

            # Remove literal "\n" in source
            raw_data = raw_data.replace("\\n", "")

            try:
                metadata = json.loads(raw_data)

            except ValueError as exc:
                log.error("ValueError: Unable to convert to JSON "
                          "representation: {0}".format(exc.args))
                log.debug("Matching Source:  {0}".format(raw_data))
                pass

        log.debug("Image Metadata:\n{0}".format(pprint.pformat(metadata)))
        return metadata

    @staticmethod
    def remove_control_characters(s):
        return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")

    @staticmethod
    def _translate_unicode_in_link(link):
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
