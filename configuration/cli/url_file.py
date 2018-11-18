import datetime
import os
import pprint

from PDL.logger.logger import Logger as Log

log = Log()


class UrlFile(object):

    TIMESTAMP = r'%y%m%d_%H%M%S'
    URL_LIST_DELIM = 'CLI LIST'
    URL_DELIM = ' '

    def write_file(self, urls, location, filename=None):
        if filename is None:
            timestamp = datetime.datetime.now().strftime(self.TIMESTAMP)
            filename = '{0}.input'.format(timestamp)
        filespec = os.path.abspath(os.path.join(location, filename))
        log.info("Writing url input to file: {loc}".format(loc=filespec))

        with open(filespec, 'w') as FILE:
            FILE.write("URL LIST:\n")
            for index, url in enumerate(urls):
                FILE.write("{index:>3}) {url}\n".format(
                    index=index + 1, url=url))
            FILE.write("\n{url_list_delim}:\n".format(
                url_list_delim=self.URL_LIST_DELIM))
            FILE.write("{0}\n".format(self.URL_DELIM.join(urls)))

        log.info("Wrote urls ({num}) to the input file: {loc}".format(
            loc=filespec, num=len(urls)))

        return filespec

    def read_file(self, filename):
        if not os.path.exists(os.path.abspath(filename)):
            log.error("Unable to find input file: {0}".format(filename))
            return list()

        log.info('Reading url file: {0}'.format(filename))
        with open(filename, "r") as FILE:
            lines = FILE.readlines()

        url_list = list()

        log.info("Number of URLs found: {0}".format(len(lines)))
        for index in range(len(lines)):
            if self.URL_LIST_DELIM in lines[index]:
                url_list = [x.strip() for x in
                            lines[index + 1].split(self.URL_DELIM)]
                break

        log.debug("URLs Found in File:\n{0}".format(pprint.pformat(url_list)))

        return url_list

