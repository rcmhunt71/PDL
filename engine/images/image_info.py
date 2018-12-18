import json
import pprint

from PDL.engine.images.status import (
    DownloadStatus as Status,
    ImageDataModificationStatus as ModStatus
)


class ImageData(object):
    def __init__(self):
        self.image_name = None
        self.description = None
        self.page_url = None
        self.image_url = None
        self.author = None
        self.filename = None
        self.image_date = None
        self.resolution = None
        self.downloaded_on = None
        self.download_duration = None
        self.locations = list()
        self.dl_status = Status.NOT_SET
        self.mod_status = ModStatus.NEW
        self.error_info = None

    def to_json(self):
        attributes = self._list_attributes()
        attr_dict = dict([(key, getattr(self, key)) for key in attributes])

        pprint.pprint(attr_dict)

        return json.dumps(attr_dict)

    def _list_attributes(self):
        return [x for x in dir(self) if not x.startswith('_')
                and x.lower() == x and not callable(getattr(self, x))]
