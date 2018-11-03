class DownloadStatus(object):
    NOT_SET = 'Not Set'
    PENDING = 'Pending'
    DOWNLOADED = 'Downloaded'
    IN_DATABASE = "In_Database"
    EXISTS = 'Exists'
    ERROR = 'Error'


class ImageDataModificationStatus(object):
    NEW = "New"
    UPDATED = "Updated"
    DELETE = "Delete"
