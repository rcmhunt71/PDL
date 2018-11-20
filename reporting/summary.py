from PDL.engine.images.status import DownloadStatus

import prettytable


class ReportingSummary(object):
    def __init__(self, image_data):
        self.data = image_data
        self.tally = self._init_tally_dict()

    def tally_results(self):
        for image in self.data:
            self.tally[image.dl_status] += 1
        return self.tally

    @staticmethod
    def _init_tally_dict():
        return dict([(getattr(DownloadStatus, status), 0) for status in
                     dir(DownloadStatus) if not status.startswith('_')])

    def results_table(self):

        status_header = 'Status'
        count_header = 'Count'

        table = prettytable.PrettyTable()
        table.field_names = [status_header, count_header]
        for status, count in self.tally.items():
            table.add_row([status, count])
        table.sortby = count_header
        table.reversesort = True
        table.align[count_header] = 'r'
        table.align[status_header] = 'l'
        return table.get_string(title='Download Status')
