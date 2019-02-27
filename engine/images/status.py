from typing import List


class Constants(object):
    @classmethod
    def get_statuses(cls) -> List[str]:
        return [status for status in sorted(dir(cls)) if
                (not status.startswith('_') and not callable(getattr(cls, status)) and status.lower() != status)]


class DownloadStatus(Constants):
    NOT_SET = 'Status_Not_Set'
    PENDING = 'Pending'
    DOWNLOADED = 'Downloaded'
    IN_DATABASE = "In_Database"
    EXISTS = 'Exists'
    ERROR = 'Error'


class ImageDataModificationStatus(Constants):
    NEW = "New"
    UPDATED = "Updated"
    DELETE = "Delete"
    MOD_NOT_SET = "Not_Set"
    UNCHANGED = 'Unchanged'
