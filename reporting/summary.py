import prettytable
from PDL.engine.images.status import DownloadStatus
from PDL.logger.logger import Logger

log = Logger()


class ReportingSummary(object):

    INT_VALUE_TYPE = 'int'
    LIST_VALUE_TYPE = 'list'
    DICT_VALUE_TYPE = 'dict'
    DEFAULT_VALUE_TYPE = INT_VALUE_TYPE

    def __init__(self, image_data):
        self.data = image_data
        self.status_tally = None
        self.url_results = None

    # ------------------- GENERAL METHODS -------------------

    @staticmethod
    def _log_table(table):
        for line in table.split('\n'):
            log.info(line)

    # ------------------- BASIC RESULT TABLE STRUCTURE -------------------

    def init_status_dict_(self, value_type=DEFAULT_VALUE_TYPE):
        init_dict = dict()
        debug_msg = "Creating status dict with '{type_}' value structure."

        statuses = DownloadStatus.get_statuses_()

        # INTEGER
        if value_type.lower() == self.INT_VALUE_TYPE:
            log.debug(debug_msg.format(type_=self.INT_VALUE_TYPE))
            init_dict = dict([(getattr(DownloadStatus, status), 0) for status in statuses])

        # LIST
        elif value_type.lower() == self.LIST_VALUE_TYPE:
            log.debug(debug_msg.format(type_=self.LIST_VALUE_TYPE))
            init_dict = dict([(getattr(DownloadStatus, status), list()) for status in statuses])

        # DICTIONARY
        elif value_type.lower() == self.DICT_VALUE_TYPE:
            log.debug(debug_msg.format(type_=self.DICT_VALUE_TYPE))
            init_dict = dict([(getattr(DownloadStatus, status), dict()) for status in statuses])

        return init_dict

    # ------------------- DOWNLOAD STATUS RESULTS -------------------

    def tally_status_results(self):
        log.debug("Tallying Download Status results.")
        status_tally = self.init_status_dict_(value_type=self.INT_VALUE_TYPE)
        for image in self.data:
            status_tally[image.dl_status] += 1
        return status_tally

    def status_table(self, recalculate=False):
        status_header = 'Status'
        count_header = 'Count'

        table = prettytable.PrettyTable()
        table.field_names = [status_header, count_header]

        if self.status_tally is None or recalculate:
            self.status_tally = self.tally_status_results()

        log.debug("Building Download Status Results table.")
        for status, count in self.status_tally.items():
            table.add_row([status.upper(), count])

        table.sortby = status_header
        table.reversesort = False
        table.align[count_header] = 'r'
        table.align[status_header] = 'l'
        return table.get_string(title='Download Status')

    def log_download_status_results_table(self, recalculate=False):
        self._log_table(table=self.status_table(recalculate=recalculate))

    # ------------------- URL RESULTS -------------------

    def tally_url_results(self):
        log.debug("Tallying URL results.")
        url_results = self.init_status_dict_(value_type=self.LIST_VALUE_TYPE)
        for image in self.data:
            url_results[image.dl_status].append(image.image_url)
        return url_results

    def url_results_table(self, specific_status=None, recalculate=False):

        delimiter = '   + '
        url_header = "URL"
        table = prettytable.PrettyTable()
        table.field_names = [url_header]
        table.align[url_header] = 'l'

        log.debug("Displaying specific status: '{0}'".format(str(specific_status).upper()))

        if self.url_results is None or recalculate:
            self.url_results = self.tally_url_results()

        log.debug("Building URL results table.")
        for status, urls in sorted(self.url_results.items()):
            if specific_status is None or specific_status.lower() == status.lower():
                table.add_row(["{status} ({count})".format(
                    status=status.upper(), count=len(urls))])
                [table.add_row(["{delim}{url}".format(
                    url=url, delim=delimiter)]) for url in urls]
        return table.get_string(title='URL Status')

    def log_url_status_table(self, specific_status=None, recalculate=False):
        self._log_table(
            table=self.url_results_table(
                specific_status=specific_status, recalculate=recalculate))

# ------------------- TODOs -------------------
# TODO: <code> Add report about errors, and link info
# TODO: <code> Create JSON report of DL'd info.
