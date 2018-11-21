class DownloadStatus(object):
    NOT_SET = 'Not Set'
    PENDING = 'Pending'
    DOWNLOADED = 'Downloaded'
    IN_DATABASE = "In_Database"
    EXISTS = 'Exists'
    ERROR = 'Error'

    @staticmethod
    def get_statuses_():
        return [x for x in dir(DownloadStatus) if (
                not x.startswith('_') or not x.endswith('_'))]


class ImageDataModificationStatus(object):
    NEW = "New"
    UPDATED = "Updated"
    DELETE = "Delete"
