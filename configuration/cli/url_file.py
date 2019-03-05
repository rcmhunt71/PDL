"""

   Classes and routines for reading and writing of URL files.

   URL files are a list of (valid) URLs provided to the application: the file
   contains an indexed list of the URLs and a space-delimited list of URLs for
   cut-and-paste or replay.

"""

import datetime
import os
import pprint
from typing import List, Optional

from PDL.configuration.cli.urls import UrlArgProcessing
from PDL.logger.logger import Logger as Log
import PDL.logger.utils as utils

LOG = Log()


class UrlFile:
    """

    This class is for reading and writing of URL files.

    URL files are a list of (valid) URLs provided to the application: the file
    contains an indexed list of the URLs and a space-delimited list of URLs for
    cut-and-paste or replay.

    """
    TIMESTAMP = r'%y%m%d_%H%M%S'
    URL_LIST_DELIM = 'CLI LIST'
    URL_DELIM = ' '
    EXTENSION = 'urls'

    def write_file(self, urls: List[str], location: str, filename: Optional[str] = None,
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
        LOG.debug(f"Writing url input to file: {filespec}")
        with open(filespec, 'w') as url_file:
            url_file.write("URL LIST:\n")
            for index, url in enumerate(urls):
                url_file.write(f"{index + 1:>3}) {url}\n")
            url_file.write(f"\n{self.URL_LIST_DELIM}:\n")
            url_file.write(f"{self.URL_DELIM.join(urls)}\n")

        LOG.info(f"Wrote urls to the input file: {filespec} --> ({len(urls)} urls)")

        return filespec

    def read_file(self, filename: str) -> List[str]:
        """
        Read URL save file into list
        :param filename: (str) path and name of file.

        :return: (list) List of URLs

        """
        # Check if file exists, return empty list if it does not.
        if not os.path.exists(os.path.abspath(filename)):
            LOG.error(f"Unable to find input file: {filename}")
            return list()

        # Read file
        LOG.info(f'Reading url file: {filename}')
        with open(filename, "r") as url_file:
            lines = url_file.readlines()

        # Split file entry into list
        url_list = list()
        for line in lines:
            if line.strip().startswith(UrlArgProcessing.PROTOCOL):
                url_list.extend([x.strip() for x in line.split(self.URL_DELIM)])

        urls = pprint.pformat(url_list)
        LOG.debug(f"URLs Found in File:\n{urls}")
        return url_list
