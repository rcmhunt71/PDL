try:
    # Python 2.7+
    from unittest.mock import patch, create_autospec
except ImportError:
    from mock import patch, create_autospec


import os
import requests
import tempfile

import PDL.engine.download.pxSite1.download_image as dl
import PDL.engine.images.image_info as imageinfo
import PDL.engine.images.status as status

from nose.tools import assert_equals


def create_temp_file(size=1024):
    file_obj = tempfile.NamedTemporaryFile(mode="w", suffix='jpg', delete=False)
    file_obj.write("*" * size)
    file_obj.close()
    return file_obj


class TestDownloadPX(object):

    DELIM = "sig="
    IMAGE_NAME = 'this_is_my_name'
    DUMMY_URL_FMT = "https://wooba.com/help/{delim}{image}"
    DUMMY_URL = DUMMY_URL_FMT.format(delim=DELIM, image=IMAGE_NAME)

    def test_set_status_updates_all_statuses(self):

        test_status = status.DownloadStatus.DOWNLOADED

        image_dl = dl.DownloadPX(image_url=self.DUMMY_URL,
                                 url_split_token=None,
                                 dl_dir='/tmp',
                                 image_info=None)
        image_dl.status = test_status

        assert_equals(image_dl.status, test_status)
        assert_equals(image_dl.image_info.dl_status, test_status)

    def test_set_status_on_provided_imagedata_obj(self):

        test_status = status.DownloadStatus.DOWNLOADED

        image_data = imageinfo.ImageData()
        image_data.dl_status = status.DownloadStatus.PENDING

        image_dl = dl.DownloadPX(image_url=self.DUMMY_URL,
                                 url_split_token=None,
                                 dl_dir='/tmp',
                                 image_info=image_data)
        image_dl.status = test_status

        assert_equals(image_dl.status, test_status)
        assert_equals(image_dl.image_info.dl_status, test_status)

    def test_get_image_name_without_url_returns_none(self):
        image_dl = dl.DownloadPX(image_url=None,
                                 url_split_token=None,
                                 dl_dir='/tmp')
        name = image_dl.get_image_name()
        assert_equals(name, None)
        assert_equals(image_dl.status, status.DownloadStatus.ERROR)

    def test_get_image_name_with_wget(self):
        image_dl = dl.DownloadPX(image_url=self.DUMMY_URL,
                                 url_split_token=None,
                                 dl_dir='/tmp')
        name = image_dl.get_image_name(use_wget=True)
        assert_equals(name, '{0}.{1}'.format(
            self.IMAGE_NAME, dl.DownloadPX.EXTENSION))
        assert_equals(image_dl.status, status.DownloadStatus.PENDING)

    def test_get_image_name_with_no_image(self):
        image_dl = dl.DownloadPX(image_url='https://abc.com/',
                                 url_split_token=None,
                                 dl_dir='/tmp')
        name = image_dl.get_image_name()
        assert_equals(image_dl.status, status.DownloadStatus.ERROR)
        assert_equals(name, None)

# -----------------------------------------------------------------------
# ---------------------- DOWNLOAD VIA REQUESTS --------------------------
# -----------------------------------------------------------------------

    class MockedContent(object):
        """
        A simple object built to mock object built during processing requests
        socket response.
        """
        def __init__(self, decode=False):
            self.decode_content = decode

    mocked_get_response_proper = create_autospec(requests.Response)
    mocked_get_response_proper.status_code = 200
    mocked_get_response_proper.raw = MockedContent()

    def mocked_shutils_copyfileobj(self, arg1, arg2):
        """
        Don't copy anything, just act as a pass-though
        :param arg1: copyfileobj has 2 args. This is the first.
        :param arg2: copyfileobj has 2 args. This is the second.

        :return: None. This function is a no-op

        """
        pass

    @patch('PDL.engine.download.pxSite1.download_image.requests.get',
           return_value=mocked_get_response_proper)
    @patch('PDL.engine.download.pxSite1.download_image.shutil.copyfileobj',
           return_value=mocked_shutils_copyfileobj)
    def test_dl_via_requests_200(self, copyfileobj, requests_get):

        temp_file = tempfile.NamedTemporaryFile(mode='r', delete=True)
        print("Created temp file: {0}".format(temp_file.name))

        image_obj = dl.DownloadPX(image_url=self.DUMMY_URL, dl_dir='/tmp')
        image_obj.dl_file_spec = temp_file.name
        dl_status = image_obj.dl_via_requests()

        temp_file.close()
        print("Closed/Removed temp file: {0}".format(image_obj.dl_file_spec))

        assert requests_get.call_count == 1
        assert copyfileobj.call_count == 1
        assert image_obj.status == status.DownloadStatus.DOWNLOADED
        assert dl_status == status.DownloadStatus.DOWNLOADED

    mocked_get_response_proper = create_autospec(requests.Response)
    mocked_get_response_proper.status_code = 404
    mocked_get_response_proper.raw = MockedContent()

    @patch('PDL.engine.download.pxSite1.download_image.requests.get',
           return_value=mocked_get_response_proper)
    @patch('PDL.engine.download.pxSite1.download_image.shutil.copyfileobj',
           return_value=mocked_shutils_copyfileobj)
    def test_dl_via_requests_404(self, copyfileobj, requests_get):

        temp_file = tempfile.NamedTemporaryFile(mode='r', delete=True)
        print("Created temp file: {0}".format(temp_file.name))

        image_obj = dl.DownloadPX(image_url=self.DUMMY_URL, dl_dir='/tmp')
        image_obj.dl_file_spec = temp_file.name

        assert image_obj.status == status.DownloadStatus.PENDING

        dl_status = image_obj.dl_via_requests()

        temp_file.close()
        print("Closed/removed temp file: {0}".format(image_obj.dl_file_spec))

        assert requests_get.call_count == 1
        assert copyfileobj.call_count == 0
        assert image_obj.status == status.DownloadStatus.ERROR
        assert dl_status == status.DownloadStatus.ERROR

# -----------------------------------------------------------------------
# ------------------------ DOWNLOAD VIA WGET ----------------------------
# -----------------------------------------------------------------------

    wget_tmp_file_obj_min_size = create_temp_file(
        size=(dl.DownloadPX.MIN_KB + 1) * dl.DownloadPX.KILOBYTES)
    wget_tmp_file_obj_5k = create_temp_file(size=(5 * dl.DownloadPX.KILOBYTES))
    wget_tmp_file_obj_conn_error = create_temp_file(
        size=(dl.DownloadPX.MIN_KB + 1) * dl.DownloadPX.KILOBYTES)
    wget_tmp_file_wget_disabled = create_temp_file(
        size=(dl.DownloadPX.MIN_KB + 1) * dl.DownloadPX.KILOBYTES)

    @patch('PDL.engine.download.pxSite1.download_image.wget.download',
           return_value=wget_tmp_file_obj_min_size.name)
    def test_dl_via_wget_200_with_correct_file_size(self, wget_mock):

        image_file = wget_mock.return_value
        print("Created temp file: {0}".format(image_file))
        print("Temp file stats:\n\tSize:{size} bytes".format(
            size=os.path.getsize(image_file)))

        image_obj = dl.DownloadPX(
            image_url=self.DUMMY_URL, dl_dir='/tmp', use_wget=True)
        image_obj.RETRY_DELAY = 0
        assert image_obj.status == status.DownloadStatus.PENDING

        dl_status = image_obj.dl_via_wget()
        os.remove(wget_mock.return_value)

        print("Deleted temp file: {0}".format(image_file))
        print("Mock call count: {0}".format(wget_mock.call_count))

        assert wget_mock.call_count == 1
        assert dl_status == status.DownloadStatus.DOWNLOADED
        assert image_obj.status == status.DownloadStatus.DOWNLOADED
        assert image_obj.image_info.dl_status == status.DownloadStatus.DOWNLOADED

    @patch('PDL.engine.download.pxSite1.download_image.wget.download',
           return_value=wget_tmp_file_obj_5k.name)
    @patch('PDL.engine.download.pxSite1.download_image.os.remove',
           return_value=None)
    def test_dl_via_wget_200_with_incorrect_file_size(
            self, mock_delete, wget_mock):

        image_file = wget_mock.return_value
        print("Created temp file: {0}".format(image_file))
        print("Temp file stats:\n\tSize:{size} bytes".format(
            size=os.path.getsize(image_file)))

        image_obj = dl.DownloadPX(
            image_url=self.DUMMY_URL, dl_dir='/tmp', use_wget=True)
        image_obj.RETRY_DELAY = 0
        assert image_obj.status == status.DownloadStatus.PENDING

        dl_status = image_obj.dl_via_wget()
        os.remove(wget_mock.return_value)

        print("Deleted temp file: {0}".format(image_file))
        print("Mock WGET call count: {0}".format(wget_mock.call_count))
        print("Mock delete call count: {0}".format(mock_delete.call_count))

        assert wget_mock.call_count == dl.DownloadPX.MAX_ATTEMPTS
        assert mock_delete.call_count == dl.DownloadPX.MAX_ATTEMPTS + 1
        assert dl_status == status.DownloadStatus.ERROR
        assert image_obj.status == status.DownloadStatus.ERROR
        assert image_obj.image_info.dl_status == status.DownloadStatus.ERROR

        # TODO: Move delete patch to context manager to allow proper os.remove()

    @patch('PDL.engine.download.pxSite1.download_image.wget.download',
           return_value=wget_tmp_file_obj_conn_error.name,
           side_effect=requests.exceptions.ConnectionError())
    def test_dl_via_wget_conn_err(
            self, wget_mock):

        image_file = wget_mock.return_value
        print("Created temp file: {0}".format(image_file))
        print("Temp file stats:\n\tSize:{size} bytes".format(
            size=os.path.getsize(image_file)))

        image_obj = dl.DownloadPX(
            image_url=self.DUMMY_URL, dl_dir='/tmp', use_wget=True)
        image_obj.RETRY_DELAY = 0
        assert image_obj.status == status.DownloadStatus.PENDING

        dl_status = image_obj.dl_via_wget()

        print("Deleted temp file: {0}".format(image_file))
        print("Mock WGET call count: {0}".format(wget_mock.call_count))

        assert wget_mock.call_count == dl.DownloadPX.MAX_ATTEMPTS
        assert dl_status == status.DownloadStatus.ERROR
        assert image_obj.status == status.DownloadStatus.ERROR
        assert image_obj.image_info.dl_status == status.DownloadStatus.ERROR

    @patch('PDL.engine.download.pxSite1.download_image.wget.download',
           return_value=wget_tmp_file_wget_disabled)
    def test_dl_via_wget_but_wget_is_disabled(self, wget_mock):

        image_obj = dl.DownloadPX(
            image_url=self.DUMMY_URL, dl_dir='/tmp', use_wget=False)
        image_obj.RETRY_DELAY = 0
        image_obj.MAX_ATTEMPTS = 0
        assert image_obj.status == status.DownloadStatus.PENDING

        dl_status = image_obj.dl_via_wget()

        print("Mock WGET call count: {0}".format(wget_mock.call_count))

        assert wget_mock.call_count == image_obj.MAX_ATTEMPTS
        assert dl_status == status.DownloadStatus.ERROR
        assert image_obj.status == status.DownloadStatus.ERROR
        assert image_obj.image_info.dl_status == status.DownloadStatus.ERROR

# -----------------------------------------------------------------------
# --------------------------- file_exists  ------------------------------
# -----------------------------------------------------------------------

    def test_filespec_is_none(self):
        image_obj = dl.DownloadPX(
            image_url=self.DUMMY_URL, dl_dir='/tmp', use_wget=True)
        image_obj.dl_file_spec = None

        result = image_obj.file_exists()
        assert result is False
        assert image_obj.status == status.DownloadStatus.ERROR

    def test_filespec_is_empty_string(self):
        image_obj = dl.DownloadPX(
            image_url=self.DUMMY_URL, dl_dir='/tmp', use_wget=True)
        image_obj.dl_file_spec = ''

        result = image_obj.file_exists()
        assert result is False
        assert image_obj.status == status.DownloadStatus.ERROR

    def test_filespec_is_valid(self):
        temp_file = create_temp_file(
            size=(dl.DownloadPX.MIN_KB + 1) * dl.DownloadPX.KILOBYTES)

        image_obj = dl.DownloadPX(
            image_url=self.DUMMY_URL, dl_dir='/tmp', use_wget=True)
        image_obj.dl_file_spec = temp_file.name

        result = image_obj.file_exists()
        os.remove(temp_file.name)

        assert result is True
        assert image_obj.status == status.DownloadStatus.EXISTS

    def test_filespec_does_not_exist(self):

        image_obj = dl.DownloadPX(
            image_url=self.DUMMY_URL, dl_dir='/tmp', use_wget=True)
        image_obj.dl_file_spec = '/tmp/does_not_exist.wooba'
        curr_status = image_obj.status

        result = image_obj.file_exists()
        assert result is False
        assert image_obj.status == curr_status

# -----------------------------------------------------------------------
# --------------------------- download_image ----------------------------
# -----------------------------------------------------------------------

    @patch('PDL.engine.download.pxSite1.download_image.DownloadPX.dl_via_requests',
           return_value=status.DownloadStatus.PENDING)
    def test_download_image_unable_to_dl(self, dl_pending_mock):
        dl_image = dl.DownloadPX(image_url=self.DUMMY_URL, dl_dir='/tmp')
        dl_image.RETRY_DELAY = 0
        dl_status = dl_image.download_image()

        assert dl_status == status.DownloadStatus.PENDING
        assert dl_image.status == status.DownloadStatus.PENDING
        assert dl_pending_mock.call_count == dl.DownloadPX.MAX_ATTEMPTS

    @patch('PDL.engine.download.pxSite1.download_image.DownloadPX.dl_via_requests',
           return_value=status.DownloadStatus.DOWNLOADED)
    def test_download_image_successful_dl(self, dl_pending_mock):
        dl_image = dl.DownloadPX(image_url=self.DUMMY_URL, dl_dir='/tmp')
        dl_image.RETRY_DELAY = 0
        dl_status = dl_image.download_image()

        assert dl_status == status.DownloadStatus.DOWNLOADED
        assert dl_pending_mock.call_count == 1

    @patch('PDL.engine.download.pxSite1.download_image.DownloadPX.dl_via_wget',
           return_value=status.DownloadStatus.DOWNLOADED)
    def test_download_image_successful_dl_wget(self, dl_pending_mock):
        dl_image = dl.DownloadPX(
            image_url=self.DUMMY_URL, dl_dir='/tmp', use_wget=True)
        dl_image.RETRY_DELAY = 0
        dl_status = dl_image.download_image()

        assert dl_status == status.DownloadStatus.DOWNLOADED
        assert dl_pending_mock.call_count == 1
