import PDL.engine.download.download_base as base

from nose.tools import raises


class TestDownloadBase(object):

    IMAGE_URL = 'https://foo.bar/'
    DL_DIR = '/tmp'

    @raises(base.NotImplementedMethod)
    def test_parse_image_info_definition(self):
        method_name = 'parse_image_info'
        self._test_object_using_method(method_name)

    @raises(base.NotImplementedMethod)
    def test_get_image_status_definition(self):
        method_name = 'get_image_status'
        self._test_object_using_method(method_name)

    @raises(base.NotImplementedMethod)
    def test_download_image_definition(self):
        method_name = 'download_image'
        self._test_object_using_method(method_name)

    def _test_object_using_method(self, method_name):
        dl = base.DownloadImage(image_url=self.IMAGE_URL, dl_dir=self.DL_DIR)
        api = getattr(dl, method_name)
        api()

