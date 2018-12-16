import prettytable
from PDL.engine.images.status import DownloadStatus


class ReportingSummary(object):
    def __init__(self, image_data):
        self.data = image_data
        self.tally = self.init_tally_dict_()

    def tally_results(self):
        for image in self.data:
            self.tally[image.dl_status] += 1
        return self.tally

    @staticmethod
    def init_tally_dict_():
        statuses = DownloadStatus.get_statuses_()
        return dict([(getattr(DownloadStatus, status), 0) for status in statuses])

    def results_table(self):

        status_header = 'Status'
        count_header = 'Count'

        table = prettytable.PrettyTable()
        table.field_names = [status_header, count_header]
        for status, count in self.tally.items():
            table.add_row([status, count])

        # PrettyTable's get_string() is calling something that used to return an int in Python2.x,
        # but it is now a str. Need to dig into, find issue, and submit a patch.
        # TODO: Find str/int issue for prettytable in Python 3

        # table.sortby = table.field_names.index(count_header)

        table.reversesort = True
        table.align[count_header] = 'r'
        table.align[status_header] = 'l'
        return table.get_string(title='Download Status')

# TODO: <code> Add report about errors, and link info
# TODO: <code> Create JSON report of DL'd info.
