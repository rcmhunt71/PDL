from PDL.images.consts import (
    DownloadStatus,
    ImageDataModificationStatus as ModStatus
)


class ImageData(object):
    def __init__(self):
        self._image_name = None
        self._description = None
        self._page_url = None
        self._image_url = None
        self._author = None
        self._subject = None
        self._downloaded_on = None
        self._download_dur = None
        self._locations = list()
        self._dl_status = DownloadStatus.NOT_SET
        self._mod_status = ModStatus.NEW
