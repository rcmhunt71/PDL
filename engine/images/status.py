"""

  Constants - defined and grouped based on use (each within their own class)

"""

from typing import List


class Constants:
    """

      Provides a generic method for listing constants within a class.
      Assumptions: Constants are CAPITALIZED, not prefixed with an underscore, and not callable

    """
    @classmethod
    def get_statuses(cls) -> List[str]:
        """
        Returns all constants defined the class.
        Assumptions: Constants are CAPITALIZED, not prefixed with an underscore, and not callable

        :return: List of CONSTANTS defined in the class

        """
        return [status for status in sorted(dir(cls)) if
                (not status.startswith('_') and not callable(getattr(cls, status)) and
                 status.lower() != status)]


class DownloadStatus(Constants):
    """

    Constants associated with a Download Status

    """
    NOT_SET = 'Status_Not_Set'
    PENDING = 'Pending'
    DOWNLOADED = 'Downloaded'
    IN_DATABASE = "In_Database"
    EXISTS = 'Exists'
    ERROR = 'Error'


class ImageDataModificationStatus(Constants):
    """

    Constants associated with Image Data DB Record Status

    """
    NEW = "New"
    UPDATED = "Updated"
    DELETE = "Delete"
    MOD_NOT_SET = "Not_Set"
    UNCHANGED = 'Unchanged'
