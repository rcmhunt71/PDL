from PDL.images.consts import (
    DownloadStatus,
    ImageDataModificationStatus as ModStatus
)


class ImageData(object):
    def __init__(self):
        self.image_name = None
        self.description = None
        self.page_url = None
        self.image_url = None
        self.author = None
        self.subject = None
        self.downloaded_on = None
        self.download_dur = None
        self.locations = list()
        self.dl_status = DownloadStatus.NOT_SET
        self.mod_status = ModStatus.NEW

