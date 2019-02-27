from random import choice

from PDL.engine.images.image_info import ImageData
from PDL.engine.images.status import DownloadStatus as Status
from PDL.reporting.summary import ReportingSummary

data = list()
num_data = 100

statuses = Status.get_statuses()

for _ in range(num_data):
    dummy_image = ImageData()
    dummy_image.dl_status = getattr(Status, choice(statuses))
    data.append(dummy_image)


class TestReportingSummary(object):

    def test_reporting_summary_values(self):
        summary = ReportingSummary(image_data=data)
        results = summary.tally_status_results()

        data_tally = summary.init_status_dict_()
        for image in data:
            data_tally[image.dl_status] += 1

        for status in statuses:
            status_value = getattr(Status, status)
            assert results[status_value] == data_tally[status_value]
