import datetime
import os
import pprint

from PDL.logger.logger import Logger as Log
import PDL.logger.utils as utils

log = Log()


class UrlFile(object):

    TIMESTAMP = r'%y%m%d_%H%M%S'
    URL_LIST_DELIM = 'CLI LIST'
    URL_DELIM = ' '
    EXTENSION = 'urls'

    def write_file(self, urls, location, filename=None, create_dir=False):
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
            return None

        # Create file name
        if filename is None:
            timestamp = datetime.datetime.now().strftime(self.TIMESTAMP)
            filename = '{0}.{1}'.format(timestamp, self.EXTENSION)
        filespec = os.path.abspath(os.path.join(location, filename))

        # Write URLs to file
        log.debug("Writing url input to file: {loc}".format(loc=filespec))
        with open(filespec, 'w') as FILE:
            FILE.write("URL LIST:\n")
            for index, url in enumerate(urls):
                FILE.write("{index:>3}) {url}\n".format(
                    index=index + 1, url=url))
            FILE.write("\n{url_list_delim}:\n".format(
                url_list_delim=self.URL_LIST_DELIM))
            FILE.write("{0}\n".format(self.URL_DELIM.join(urls)))

        log.info("Wrote urls to the input file: {loc} --> ({num} urls) ".format(
            loc=filespec, num=len(urls)))

        return filespec

    def read_file(self, filename):
        """
        Read URL save file into list
        :param filename: (str) path and name of file.

        :return: (list) List of URLs

        """

        # Check if file exists, return empty list if it does not.
        if not os.path.exists(os.path.abspath(filename)):
            log.error("Unable to find input file: {0}".format(filename))
            return list()

        # Read file
        log.info('Reading url file: {0}'.format(filename))
        with open(filename, "r") as FILE:
            lines = FILE.readlines()

        url_list = list()

        # Split file entry into list
        log.info("Number of URLs found: {0}".format(len(lines)))
        for index in range(len(lines)):
            if self.URL_LIST_DELIM in lines[index]:
                url_list = [x.strip() for x in
                            lines[index + 1].split(self.URL_DELIM)]
                break

        log.debug("URLs Found in File:\n{0}".format(pprint.pformat(url_list)))

        return url_list
