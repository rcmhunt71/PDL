import PDL.engine.download.pxSite1.download_image as dl
import PDL.engine.images.image_info as imageinfo
import PDL.engine.images.status as status

from nose.tools import assert_equals


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

    # TODO: Test dl capability via mock
