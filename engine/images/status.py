class DownloadStatus(object):
    NOT_SET = 'Status_Not_Set'
    PENDING = 'Pending'
    DOWNLOADED = 'Downloaded'
    IN_DATABASE = "In_Database"
    EXISTS = 'Exists'
    ERROR = 'Error'

    @staticmethod
    def get_statuses_():
        return [x for x in dir(DownloadStatus) if (
            (not x.startswith('_') or not x.endswith('_')) and x.lower() != x)]


class ImageDataModificationStatus(object):
    NEW = "New"
    UPDATED = "Updated"
    DELETE = "Delete"
    MOD_NOT_SET = "Not_Set"
    UNCHANGED = 'Unchanged'
