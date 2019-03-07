"""
This module creates the various prettyTable tables used within the application.

NOTE: There is a wrapper function _log_table that will process a string_version of
   the table and record it into the logs (at requested or default level)

"""

from typing import Dict, List, Optional

from PDL.engine.images.image_info import ImageData
from PDL.engine.images.status import DownloadStatus
from PDL.logger.logger import Logger

import prettytable

LOG = Logger()


class ReportingSummary:

    """
    Builds various reports for DL'd images, leveraging the data in
    the ImageData objects.
    """

    # Used for initializing a dictionary with values of <type>
    # Allows to dynamically set the expected value type
    INT_VALUE_TYPE = 'int'
    LIST_VALUE_TYPE = 'list'
    DICT_VALUE_TYPE = 'dict'
    DEFAULT_VALUE_TYPE = INT_VALUE_TYPE
    DEFAULT_LOG_LEVEL = 'info'

    def __init__(self, image_data: List[ImageData]) -> None:
        self.data = image_data
        self.status_tally = None
        self.url_results = None

    # ------------------- GENERAL METHODS -------------------

    @staticmethod
    def log_table(table: str, log_level: str = DEFAULT_LOG_LEVEL) -> None:
        """
        Break table into separate log lines.

        :param table: Multi-line text table (delimiter = \n)
        :param log_level: Log level to log table as... (str: info, debug, error, etc.)

        :return: None
        """

        # Try to get requested logger level call
        log_call = getattr(LOG, log_level.lower(), None)

        # If None, report error and use default level.
        if log_call is None:
            LOG.error(f"Unable to log at level '{log_level.lower()}', "
                      f"defaulting to '{ReportingSummary.DEFAULT_LOG_LEVEL}'")
            log_call = getattr(LOG, ReportingSummary.DEFAULT_LOG_LEVEL, None)

        # Record the log in the tables
        # Temporarily adjust log depth by 1 , so routine that created table is
        # logged, not this routine (which only prints the table)
        log_depth = LOG.depth
        LOG.depth += 1
        for line in table.split('\n'):
            log_call(line)
        LOG.depth = log_depth

    # ------------------- BASIC RESULT TABLE STRUCTURE -------------------

    def init_status_dict_(self, value_type: str = DEFAULT_VALUE_TYPE) -> dict:
        """
        Initialize a dictionary with values of a specific type

        :param value_type: One of INT_VALUE_TYPE, LIST_VALUE_TYPE, DICT_VALUE_TYPE

        :return: Dictionary

        """
        init_dict = dict()
        debug_msg = "Creating status dict with '{type_}' value structure."

        # Get a list of all the possible statuses
        statuses = DownloadStatus.get_statuses()

        # Value Type = INTEGER
        if value_type.lower() == self.INT_VALUE_TYPE:
            LOG.debug(debug_msg.format(type_=self.INT_VALUE_TYPE))
            init_dict = {getattr(DownloadStatus, status): 0 for status in statuses}

        # Value Type = LIST
        elif value_type.lower() == self.LIST_VALUE_TYPE:
            LOG.debug(debug_msg.format(type_=self.LIST_VALUE_TYPE))
            init_dict = {getattr(DownloadStatus, status): list() for status in statuses}

        # Value Type = DICTIONARY
        elif value_type.lower() == self.DICT_VALUE_TYPE:
            LOG.debug(debug_msg.format(type_=self.DICT_VALUE_TYPE))
            init_dict = {getattr(DownloadStatus, status): dict() for status in statuses}

        return init_dict

    # ------------------- DOWNLOAD STATUS RESULTS -------------------

    def tally_status_results(self) -> Dict[str, int]:
        """
        Tally the counts of DLs based on the status

        :return: Dictionary (key: status type, value: total count)

        """
        LOG.debug("Tallying Download Status results.")
        status_tally = self.init_status_dict_(value_type=self.INT_VALUE_TYPE)

        # Iterate through all ImageData objects, and
        # add to the tally based on the ImageData.dl_status
        for image in self.data:
            status_tally[image.dl_status] += 1

        return status_tally

    def status_table(self, recalculate: bool = False) -> str:
        """
        Generate a table based on the tallied status

        :param recalculate: Recalculate tally before building table (DEFAULT: False)

        :return: (Str) Table of status + count

        +==========+=======+
        |  STATUS  | COUNT |
        +==========+=======+
        | Status 1 |   8   |
        | Status 2 |   2   |
        |   ...    |   .   |
        +==========+=======+

        """
        status_header = 'Status'
        count_header = 'Count'

        # Define table and headers
        table = prettytable.PrettyTable()
        table.field_names = [status_header, count_header]

        # Recalculate if needed or requested
        if self.status_tally is None or recalculate:
            self.status_tally = self.tally_status_results()

        # Populate table
        LOG.debug("Building Download Status Results table.")
        for status, count in self.status_tally.items():
            table.add_row([status.upper(), count])

        # Format table...
        table.sortby = status_header
        table.reversesort = False
        table.align[count_header] = 'r'
        table.align[status_header] = 'l'

        # Return string representation of table
        return table.get_string(title='Download Status')

    def log_download_status_results_table(self, recalculate: bool = False) -> None:
        """
        Generate results table and display/log the table.
        :param recalculate: Recalculate tally before building table (DEFAULT: False)
        :return: None

        """
        self.log_table(table=self.status_table(recalculate=recalculate))

    # ------------------- URL RESULTS -------------------

    def detailed_download_results_table(self, specific_status: Optional[str] = None) -> str:
        """
        Generates a table of download statuses, and the DL'd links for each status

        :param specific_status: Generate the table for a specific status

        :return: (Str) Table of status + count + links/statur

        +==================+============+
        |  STATUS/LINKS    |  Duration  |
        +==================+============+
        | Status 1  (2)    |            |
        |    - link1       | 0.250 sec  |
        |    - link2       | 0.500 sec  |
        |                  | 0.750 sec  |
        |                  |            |
        | Status 2  (4)    |            |
        |    - link3       | 0.750 sec  |
        |    - link4       | 1.250 sec  |
        |    - link5       | 0.500 sec  |
        |    - link6       | 0.750 sec  |
        |                  | 3.250 sec  |
        |                  |            |
        | ...              | ...        |
        +==================+============+
        """

        # Define various aspects of the table
        delimiter = '   - '
        image_header = "Image"
        time_format = "{0:0.3f} sec"
        duration_header = "Duration"

        # Define table, headers, and format
        table = prettytable.PrettyTable()
        table.field_names = [image_header, duration_header]
        table.align[image_header] = 'l'

        # Aggregating data
        data_dict = self.init_status_dict_(value_type='list')
        for image in self.data:
            data_dict[image.dl_status].append(image)

        if specific_status is not None:
            LOG.debug(f"Displaying specific status: '{str(specific_status).upper()}'")

        LOG.debug("Building URL results table.")
        total_dur = 0.0

        # Iterate through data, scanning for status types and corresponding links
        for status, image_obj_list in sorted(data_dict.items()):

            # Develop the status header... (either specific one (filter) or all (specific=None)
            if specific_status is None or specific_status.lower() == status.lower():
                table.add_row([f"{status.upper()} ({len(image_obj_list)})", ''])
                status_dur = 0.0

                # Add each link and DL duration that corresponds to the status
                for image in image_obj_list:
                    table.add_row([
                        "{delim}{url}".format(
                            url='{name}'.format(
                                name=image.filename if image.filename is not None else
                                image.page_url),

                            delim=delimiter),
                        time_format.format(image.download_duration)])

                    status_dur += image.download_duration
                    total_dur += image.download_duration

                table.add_row(["", time_format.format(status_dur)])
                table.add_row(["", ""])
        table.add_row(["TOTAL DURATION", time_format.format(total_dur)])
        return table.get_string(title='URL Status')

    def log_detailed_download_results_table(self, specific_status: Optional[str] = None) -> None:
        """
        Generate the detailed results table, and log to file.

        :param specific_status: Specific status to summarize
              (DEFAULT = None, implying summarize all statuses)

        :return: None

        """
        self.log_table(
            table=self.detailed_download_results_table(specific_status=specific_status))

    def error_table(self) -> str:
        """
        Build a table listing all DL errors

        :return:   (Str) Table of Image + URL + Error

        +===============+==========================+======================+
        |  Image Name   | URL                      | Error                |
        +===============+==========================+======================+
        |  image1.jpg   | www.foo.com/image1.html  | 404 - File Not Found |
        |  image2.jpg   | www.foo.com/image2.html  | 401 - Not Authorized |
        +===============+==========================+======================+

        """
        image_header = "Image Name"
        url_header = "URL"
        status_header = "Error"

        # Define table
        table = prettytable.PrettyTable()
        table.field_names = [image_header, status_header, url_header]
        table.align[image_header] = 'l'
        table.align[status_header] = 'l'
        table.align[url_header] = 'l'

        # Collect all ImageData objects that have a dl_status of ERROR.
        data = [x for x in self.data if
                x.dl_status == DownloadStatus.ERROR]

        # Populate table
        for image in data:

            # For images that could not be DL'd, list parent page
            if image.image_url is None:
                image.image_url = image.page_url

            # Add the current error to the table
            table.add_row(
                [image.image_name, image.error_info, image.image_url])

        return table.get_string(title='Download Errors')
