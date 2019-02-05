import datetime
import datetime
import os
import pprint

from PDL.configuration.cli.urls import UrlArgProcessing
from PDL.logger.logger import Logger as Log
import PDL.logger.utils as utils

log = Log()


class UrlFile(object):

    TIMESTAMP = r'%y%m%d_%H%M%S'
    URL_LIST_DELIM = 'CLI LIST'
    URL_DELIM = ' '
    EXTENSION = 'urls'

    def write_file(self, urls: list, location: str, filename: str = None,
                   create_dir: bool = False) -> str:
        """
        Write the URL list to file. Human readable, but machine parse-able.
        :param urls: (list) List of URLs to record
        :param location: (str) Location to store url file
        :param filename: (str) Name of file (use timestamp if none specified)
        :param create_dir: (bool) Create the location if it does not exist
                                  (default = False)

        :return: (str) Name and path to file

        """
        # Check if location exists, create if requested
        if not utils.check_if_location_exists(
                location=location, create_dir=create_dir):
            return ''

        # Create file name
        if filename is None:
            timestamp = datetime.datetime.now().strftime(self.TIMESTAMP)
            filename = f'{timestamp}.{self.EXTENSION}'
        filespec = os.path.abspath(os.path.join(location, filename))

        # Write URLs to file
        log.debug(f"Writing url input to file: {filespec}")
        with open(filespec, 'w') as FILE:
            FILE.write("URL LIST:\n")
            for index, url in enumerate(urls):
                FILE.write(f"{index + 1:>3}) {url}\n")
            FILE.write(f"\n{self.URL_LIST_DELIM}:\n")
            FILE.write(f"{self.URL_DELIM.join(urls)}\n")

        log.info(f"Wrote urls to the input file: {filespec} --> ({len(urls)} urls)")

        return filespec

    def read_file(self, filename: str) -> list:
        """
        Read URL save file into list
        :param filename: (str) path and name of file.

        :return: (list) List of URLs

        """
        # Check if file exists, return empty list if it does not.
        if not os.path.exists(os.path.abspath(filename)):
            log.error(f"Unable to find input file: {filename}")
            return list()

        # Read file
        log.info(f'Reading url file: {filename}')
        with open(filename, "r") as FILE:
            lines = FILE.readlines()

        # Split file entry into list
        url_list = list()
        for line in lines:
            if line.strip().startswith(UrlArgProcessing.PROTOCOL):
                url_list.extend([x.strip() for x in line.split(self.URL_DELIM)])

        urls = pprint.pformat(url_list)
        log.debug(f"URLs Found in File:\n{urls}")
        return url_list
