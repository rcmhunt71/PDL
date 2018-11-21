from random import choice

from PDL.engine.images.status import DownloadStatus as Status
from PDL.engine.images.image_info import ImageData
from PDL.reporting.summary import ReportingSummary

data = list()
num_data = 100

statuses = Status.get_statuses_()

for _ in range(num_data):
    image = ImageData()
    image.dl_status = getattr(Status, choice(statuses))
    data.append(image)


class TestReportingSummary(object):
    summary = ReportingSummary(image_data=data)
    results = summary.tally_results()

    data_tally = ReportingSummary.init_tally_dict_()
    for image in data:
        data_tally[image.dl_status] += 1

    for status in statuses:
        status_value = getattr(Status, status)
        assert results[status_value] == data_tally[status_value]
