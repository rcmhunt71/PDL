import datetime
import os
import pprint

from PDL.logger.logger import Logger as Log

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
        if not self._check_if_location_exists(
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

    @staticmethod
    def _check_if_location_exists(location, create_dir):
        """
        If the save_url directory path does not exist... Create target
        directory & all intermediate directories if 'create_dir' is True

        :param location: (str) directory path
        :param create_dir: (bool) - Create path if it does not exist

        :return: (bool) Does path exist (or was it created, if requested)

        """

        result = None
        if not os.path.exists(location):
            if create_dir:
                msg = "URL save directory '{0}' already exists"
                try:
                    os.makedirs(location)

                # Path exists
                except FileExistsError:
                    pass

                # Unexpected exception
                except Exception as exc:
                    result = False
                    log.exception(exc)

                else:
                    result = True
                    msg = "Created URL save directory: '{0}'"
                    log.debug(msg.format(location))

            # Path does not exist, but not asked to create it.
            else:
                result = False
                msg = ("URL save file directory does not exist ('{loc}'), and "
                       "was not configured to create dir.")
                log.error(msg.format(loc=location))

        # Path exists
        else:
            result = True
            log.debug("URL save file directory exists ('{loc}')".format(
                loc=location))

        return result
