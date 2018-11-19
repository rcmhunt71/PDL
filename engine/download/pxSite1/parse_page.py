import pprint
import re
import requests
import time
from six.moves.urllib.parse import quote

from PDL.engine.images.image_info import ImageData
from PDL.engine.images.page_base import CatalogPage
from PDL.engine.images.status import DownloadStatus
from PDL.logger.logger import Logger

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

    def __init__(self, page_url):
        super(CatalogPage, self).__init__(page_url=page_url)
        self.image_info = ImageData()
        self.source = None

    def get_image_info(self):
        """
        Store any collected info into the ImageData object

        :return: None

        """
        if self.source is None:
            self.source = self.get_page()

        self.image_info.page_url = self.page_url
        self.image_info.image_url = self.parse_page_for_link()
        self.image_info.author = self._get_author_name()

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

    def parse_page_for_link(self):
        """
        Retrieve the originating page, and get the desired image link out of
        the page.

        :return: Image URL that was embedded in the original page

        """

        web_url = 'web'
        www_url = '500px'

        # TODO: <TESTS> Add tests about URL prefix logic

        domain = self._get_domain_from_url().lower()
        if domain.startswith(web_url):
            return self._parse_web_url()

        elif domain.startswith(www_url):
            return self._parse_www_url()

        else:
            err_msg = ('Unrecognized domain format: {domain} - '
                       'Unsure how to proceed.')
            log.error(err_msg.format(domain=domain))
            return None

    def _get_domain_from_url(self):
        domain_pattern = r'http.://(?P<domain>(\w+\.)?\w+\.\w+)/.*'

        domain = None
        match = re.search(domain_pattern, self.page_url)
        if match is not None:
            domain = match.group('domain')
        log.debug("DOMAIN: {0}".format(domain))
        return domain

    def _parse_web_url(self):
        # TODO: <CODE> Implement web.* parsing
        log.warn('Unable to parse: {url}'.format(url=self.page_url))
        log.fatal('TO BE IMPLEMENTED: web.<domain>.<ext>')
        return None

    def _parse_www_url(self):
        url_regexp = (r'size\"\s*:\s*2048\s*,\s*\"url\"\s*:\s*\"'
                      r'(?P<url>https:.*)\"\s*,\s*\"https_url\"')

        # Reduce data to only check lines with the KEY (jpg) is found
        lines = [line for line in self.source if self.KEY in line]
        log.debug('Number of lines found with key: {key}: {num}'.format(
            key=self.KEY, num=len(lines)))
        patt = re.compile(url_regexp)

        # Try to find largest resolution image link (there are multiple links,
        # one for each size)
        for line in lines:
            result = patt.search(line)
            if result is not None:
                log.debug("Found match: {line}".format(line=line))
                link = result.group('url').replace('\/', '/')
                return self._translate_unicode_in_link(link=link)

        # If you get here, you parsed the whole page and found nada...
        self.image_info.dl_status = DownloadStatus.ERROR
        log.error('Unable to find url in source page.')
        log.error('IMAGE LINES:\n{lines}'.format(lines=lines))
        log.debug('COMPLETE SOURCE:\n{source}'.format(source=pprint.pformat(
            self.source)))
        return None

    def _get_author_name(self):
        """
        Get the author's name, if it is embedded in the page.

        :return: (str) Author's name

        """
        key = 'fullname'
        regexp_pattern = r'\s*\"fullname\"\s*:\s*\"(?P<author>.*?)\"\s*,\s*"'

        # Find all lines with the 'key' word
        lines = [line for line in self.source if key in line]

        log.debug("Matching Lines:\n{lines}".format(lines=lines))

        # Check each link for the regexp, which will contain the author's name
        for line in lines:
            result = re.search(pattern=regexp_pattern, string=line)
            if result is not None and result.group('author') != '':
                return result.group('author')

        return self.NOT_FOUND

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
