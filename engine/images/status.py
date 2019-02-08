from typing import List


class DownloadStatus(object):
    NOT_SET = 'Status_Not_Set'
    PENDING = 'Pending'
    DOWNLOADED = 'Downloaded'
    IN_DATABASE = "In_Database"
    EXISTS = 'Exists'
    ERROR = 'Error'

    @staticmethod
    def get_statuses_() -> List[str]:
        return [status for status in dir(DownloadStatus) if (
            (not status.startswith('_') or not status.endswith('_')) and status.lower() != status)]


class ImageDataModificationStatus(object):
    NEW = "New"
    UPDATED = "Updated"
    DELETE = "Delete"
    MOD_NOT_SET = "Not_Set"
    UNCHANGED = 'Unchanged'
