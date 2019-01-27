import prettytable
from PDL.engine.images.status import DownloadStatus
from PDL.logger.logger import Logger

log = Logger()


# TODO: Add Docstrings and necessary inline comments

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

    def detailed_download_results_table(self, specific_status=None):

        delimiter = '   - '
        image_header = "Image"
        time_format = "{0:0.3f} sec"
        duration_header = "Duration"
        table = prettytable.PrettyTable()
        table.field_names = [image_header, duration_header]
        table.align[image_header] = 'l'

        # Aggregating data
        data_dict = self.init_status_dict_(value_type='list')
        for image in self.data:
            data_dict[image.dl_status].append(image)

        log.debug("Displaying specific status: '{0}'".format(str(specific_status).upper()))

        log.debug("Building URL results table.")
        total_dur = 0.0
        for status, image_obj_list in sorted(data_dict.items()):
            if specific_status is None or specific_status.lower() == status.lower():
                table.add_row([
                    "{status} ({count})".format(status=status.upper(), count=len(image_obj_list)),
                    ''])
                status_dur = 0.0
                for image in image_obj_list:
                    table.add_row([
                        "{delim}{url}".format(
                            url='{name}'.format(
                                name=image.filename if image.filename is not None else image.page_url),
                            delim=delimiter),
                        time_format.format(image.download_duration)])

                    status_dur += image.download_duration
                    total_dur += image.download_duration

                table.add_row(["", time_format.format(status_dur)])
                table.add_row(["", ""])
        table.add_row(["TOTAL DURATION", time_format.format(total_dur)])
        return table.get_string(title='URL Status')

    def log_detailed_download_results_table(self, specific_status=None):
        self._log_table(
            table=self.detailed_download_results_table(specific_status=specific_status))

    def error_table(self):
        image_header = "Image Name"
        url_header = "URL"
        status_header = "Error"

        table = prettytable.PrettyTable()
        table.field_names = [image_header, status_header, url_header]

        data = [x for x in self.data if
                x.image_info.dl_status == DownloadStatus.ERROR]

        for image in data:

            # For images that could not be DL'd, list parent page
            if image.image_url is None:
                image.image_url = image.page_url

            table.add_row(
                [image.name, image.image_info.error_info, image.image_url])
        table.align[image_header] = 'l'
        table.align[status_header] = 'l'
        table.align[url_header] = 'l'
        return table.get_string(title='Download Errors')


# ------------------- TODOs -------------------
# TODO: <code> Create JSON report of DL'd info.
