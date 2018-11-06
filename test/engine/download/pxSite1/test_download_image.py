import PDL.engine.download.pxSite1.download_image as dl
import PDL.engine.images.image_info as imageinfo
import PDL.engine.images.status as status

from nose.tools import assert_equals, assert_not_equals, assert_true, assert_false


class TestDownloadPX(object):

    DUMMY_URL = "https://wooba.com/help/sig=this_is_my_name"

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
