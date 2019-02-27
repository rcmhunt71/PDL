from PDL.engine.images.status import DownloadStatus, ImageDataModificationStatus

from nose.tools import assert_equals


class TestStatuses(object):

    TEST_METHOD = 'get_statuses'

    def test_get_statuses_for_downloadstatus_class(self):
        klass = DownloadStatus
        known_statuses = {'NOT_SET', 'PENDING', 'DOWNLOADED', 'IN_DATABASE', 'EXISTS', 'ERROR'}
        self._verify_intersection_is_empty(
            target_set=known_statuses, target_class=klass)

    def test_get_statuses_for_imagedatamodificationstatus_class(self):
        klass = ImageDataModificationStatus
        known_statuses = {'NEW', 'UPDATED', 'DELETE', 'MOD_NOT_SET', 'UNCHANGED'}
        self._verify_intersection_is_empty(
            target_set=known_statuses, target_class=klass)

    def _verify_intersection_is_empty(self, target_set, target_class):
        returned_statuses = set(getattr(target_class, self.TEST_METHOD)())
        print(f"KNOWN STATUSES:\n{target_set}")
        print(f"RETURNED STATUSES:\n{returned_statuses}")

        assert_equals(target_set ^ returned_statuses, set())
