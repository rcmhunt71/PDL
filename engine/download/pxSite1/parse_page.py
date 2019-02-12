import datetime
import json
import pprint
import re
import time
from typing import List
import unicodedata

import requests
from PDL.engine.images.image_info import ImageData
from PDL.engine.images.page_base import CatalogPage
from PDL.engine.images.status import DownloadStatus
from PDL.logger.logger import Logger
from six.moves.urllib.parse import quote

log = Logger()

"""
This class will take the primary page (the display page), and parse the source code
for image specific metadata (currently in the form of an embedded JSON dictionary,
find the list of image URLs (listed by resolution), and select the URL for the 
largest available resolution.

It will also provide some basic translations for unicode.

The primary responsibility of this class is to populate the corresponding 
ImageData object, and select the URL for downloading the image directly.

"""


class ParseDisplayPage(CatalogPage):
    """
    The primary URL provided (page with image) contains several items that
    need to be scraped:
    * Image URL
    * Metadata about the image (author, resolution, name, description)
    * Image URL
    * Page URL

    This class scrapes the information contained in the page and
    instantiates/populates an ImageData object for the image.

    """

    # Browser Header - Added to request
    HEADERS = {
        'user-agent':
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'}

    RETRY_INTERVAL = 5        # Number of seconds before retrying getting page
    MAX_ATTEMPTS = 3          # Number of attempts to retrieve page
    KEY = 'jpeg'              # Delimiter on PX Page
    NOT_FOUND = 'Not Found'   # Error that may need to be scanned
    EXTENSION = 'jpg'         # Image extension

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

    def __init__(self, page_url: str) -> None:
        super(ParseDisplayPage, self).__init__(page_url=page_url)
        self.image_info = ImageData()
        self.source_list = None
        self._metadata = None

    def get_image_info(self) -> None:
        """
        Store any collected info into the ImageData object

        :return: None

        """

        # Start timer for DL measurement
        dl_start = datetime.datetime.now()

        # Get primary page source code
        if self.source_list is None:
            self.source_list = self.get_page()

            # Page info was not downloaded
            if self.source_list is None:
                self.image_info.download_duration += (datetime.datetime.now() - dl_start).total_seconds()
                log.info(f"Downloaded page in {self.image_info.download_duration:0.3f} seconds.")
                return

        # Using the page source, scrape and store the metadata (as a dictionary)
        self._metadata = self._get_metadata()

        # Calculation download duration
        self.image_info.download_duration += (datetime.datetime.now() - dl_start).total_seconds()
        log.info(f"Downloaded page in {self.image_info.download_duration:0.3f} seconds.")

        # Store the scraped metadata into the ImageData object
        self.image_info.page_url = self.page_url
        self.image_info.image_url = self.parse_page_for_link()
        self.image_info.author = self._get_author_name()
        self.image_info.image_name = self._get_title()
        self.image_info.description = self._get_description()
        self.image_info.image_date = self._get_image_date()
        self.image_info.resolution = self._get_resolution()
        self.image_info.filename = self._get_filename()
        self.image_info.id = self._get_id()

    def _get_author_name(self) -> str:
        """
        Get the Author name from the scraped metadata.

        :return: (str) Author's Name, or None if not found/set.

        """
        return self._metadata[self.PHOTO][self.USER][self.USERNAME]

    def _get_title(self) -> str:
        """
        Get the Image Title from the scraped metadata.

        :return: (str) Image Title, or None if not found/set.

        """
        return self._metadata[self.PHOTO][self.NAME]

    def _get_description(self) -> str:
        """
        Get the Image Description from the scraped metadata.

        :return: (str) Image's description, or None if not found/set.

        """
        return self._metadata[self.PHOTO][self.DESCRIPTION]

    def _get_image_date(self) -> str:
        """
        Get the Image Date from the scraped metadata.

        :return: (str) Image date, or None if not found/set.

        """
        date = datetime.datetime.fromisoformat(
            self._metadata[self.PHOTO][self.CREATED_AT])
        return str(date.isoformat()).split('.')[0]

    def _get_filename(self) -> str:
        """
        Get the file name from the image name from scraped metadata.

        :return: (str) filename of the image.

        """
        return f'{self._get_id()}.{self.EXTENSION}'

    def _get_id(self) -> str:
        """
        Get the file id from the image name URL from scraped metadata.

        :return: (str) id of the image.

        """
        url_id = (self._get_image_url() if self.image_info.image_url is None
                  else self.image_info.image_url)

        return url_id.split("=")[-1]

    def _get_resolution(self) -> str:
        """
        Build the image resolution from the scraped metadata.

        :return: (str) resolution (WxH) of the image.

        """
        width = self._metadata[self.PHOTO][self.WIDTH]
        height = self._metadata[self.PHOTO][self.HEIGHT]
        return f"{width}x{height}"

    def _get_image_url(self) -> str:
        """
        Get the image URL from the source page
        (not part of the metadata, but scraped with the metadata).

        :return: (str) URL of the actual image.

        """
        # Get the correct URL. There are multiple image URLs in the page.
        # Get the URLs from the scraped source, sort in ascending order
        # based on resolution, and get the largest image (last in the
        # sorted list)
        image_list = self._metadata[self.PHOTO][self.IMAGES]
        image_list.sort(key=lambda x: x[self.SIZE])
        target_url = image_list[-1][self.URL]

        log.debug(f"URL LIST:\n{pprint.pformat(image_list)}")
        log.debug(f"Returning URL: {target_url}")

        return target_url

    def get_page(self) -> List[str]:
        """
        Get url source code

        :return: list of source code (line by line)

        """
        conn_err = (f"{{attempt}}/{self.MAX_ATTEMPTS}: Connection Error --> Trying again in "
                    f"{self.RETRY_INTERVAL} seconds")

        attempt = 0
        source = None

        # Attempt to retrieve primary page via requests.GET()
        log_msg = "Attempt: {attempt}/{max}: Requesting page: '{url}'"
        while attempt < self.MAX_ATTEMPTS and source is None:
            attempt += 1
            log.debug(log_msg.format(
                url=self.page_url, attempt=attempt, max=self.MAX_ATTEMPTS))

            # Try to download the source page
            try:
                source = requests.get(url=self.page_url, headers=self.HEADERS)

            # D'oh!! Connection error...
            except requests.exceptions.ConnectionError:
                log.warn(conn_err.format(attempt=attempt))
                time.sleep(self.RETRY_INTERVAL)

        # If the source was downloaded and the status code was not a 200 series
        # response code, the source will not contain the required metadata.
        # (Probably received a 404 with a custom error page)
        if source is not None and int(int(source.status_code)/100) != 2:
            msg = (f"Unable to DL primary page '{self.page_url}': "
                   f"Received status code: {source.status_code}")
            log.error(msg)
            self.image_info.page_url = f"{self.page_url} ({source.status_code})"
            self.image_info.error_info = msg
            self.image_info.dl_status = DownloadStatus.ERROR
            source = None

        # Source was downloaded successfully
        elif attempt < self.MAX_ATTEMPTS:
            log.info(f"Primary page '{self.page_url}' DL'd!")

            # Split and strip the page into a list (elem per line), based on CR/LF.
            # Some pages are formatted with '\n' which made it difficult to parse at times.
            # Remove the '\n' and store as a list. The routines that need the full
            # source as a single can ''.join(<list.) as needed.
            if source is not None:
                source = [x.strip() for x in source.text.split('\n')]

        return source

    def _get_domain_from_url(self) -> str:
        """
        Get domain from the url.
        e.g - http://<domain>/resource/page.html

        :return: (str) the URL's domain

        """
        domain_pattern = r'http.://(?P<domain>(\w+\.)?\w+\.\w+)/.*'

        domain = None
        match = re.search(domain_pattern, self.page_url)
        if match is not None:
            domain = match.group('domain')
        log.debug(f"DOMAIN: {domain}")
        return domain

    def parse_page_for_link(self) -> str:
        """
        Retrieve the originating page's domain, and get
        the desired image link out of the page.

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
            err_msg = (f'Unrecognized domain format: {domain} - '
                       'Unsure how to proceed.')
            log.error(err_msg)
            self.image_info.dl_status = DownloadStatus.ERROR
            self.image_info.error_info = err_msg
            url = None

        return url

    def _get_metadata(self) -> dict:
        """
        Scrape the json metadata dictionary from the source page,
        convert to a dictionary.

        :return: dictionary of metadata (key: attribute, value: data)

        """
        metadata = dict()

        # Get PreLoaded Data, which contains image metadata
        data_pattern = r'window\.PxPreloadedData\s*=\s*(?P<data>.*?),\"comments\"'

        # Search page for match to regexp (<data> group)
        match = re.search(data_pattern, ''.join(self.source_list))

        # A match was found
        if match is not None:

            # Remove control characters
            raw_data = self.remove_control_characters(match.group('data'))

            # Adjust brace count to be zero if partial DOM is retrieved
            mismatch = raw_data.count("{") - raw_data.count("}")
            log.debug(f"Brace mismatch count: {mismatch}")
            raw_data = "{0}{1}".format(raw_data, '}' * mismatch)

            # Remove literal "\n" in source
            raw_data = raw_data.replace("\\n", "")

            # Try to convert jscr text (dict) into JSON, which
            # translates directly into a python structure (dictionary)
            try:
                metadata = json.loads(raw_data)

            except ValueError as exc:
                log.error("ValueError: Unable to convert to JSON "
                          f"representation: {exc.args}")
                log.debug(f"Matching Source:  {raw_data}")

        # Did not find a match... something has changed on the page
        # Log the source for forensic analysis
        else:
            log.error("*** Unable to parse metadata from page. ***")
            log.error(f"PAGE:\n{self.source_list}")

        log.debug(f"Image Metadata:\n{pprint.pformat(metadata)}")
        return metadata

    @staticmethod
    def remove_control_characters(s: str) -> str:
        """
        Remove any non-printing control characters from a string (breaks regexps)
        :param s: String to check/fix.
        :return: String without non-printing characters

        """
        return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")

    @staticmethod
    def _translate_unicode_in_link(link: str) -> str:
        """
        Adds quoting around unicode embedded in the links

        :param link: URL to convert/translate

        :return: Translated link

        """
        url_regexp_pattern = r'https://(?P<domain>[\w\d\.]+)/(?P<path>.*)'

        # Search link for regexp
        result = re.search(url_regexp_pattern, link)

        # Match to regexp found...
        if result is not None:
            path = quote(result.group('path'))
            link = f"https://{result.group('domain')}/{path}"

        return link
