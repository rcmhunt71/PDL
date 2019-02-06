import PDL.engine.images.page_base as base


from nose.tools import raises, assert_equals


class TestParsePageBase(object):

    IMAGE_URL = 'https://foo.bar/'

    @raises(base.NotImplementedMethod)
    def test_get_page_definition(self):
        method_name = 'get_page'
        self._test_object_using_method(method_name)

    @raises(base.NotImplementedMethod)
    def test_parse_page_for_link_definition(self):
        method_name = 'parse_page_for_link'
        self._test_object_using_method(method_name)

    @raises(base.NotImplementedMethod)
    def test_parse_page_for_link_definition(self):
        method_name = 'get_image_info'
        self._test_object_using_method(method_name)

    def _test_object_using_method(self, method_name):
        dl = base.ParsePage(page_url=self.IMAGE_URL)
        api = getattr(dl, method_name)
        api()


class TestImageContactPage(object):

    IMAGE_URL = 'https://foo.bar/'

    def test_init_params_with_list(self):
        num_urls = 10
        urls = [f'{self.IMAGE_URL}_{index}' for index in range(num_urls)]

        cpage = base.ImageContactPage(page_url=self.IMAGE_URL, image_urls=urls)
        assert_equals(len(cpage.image_urls), num_urls)

    def test_init_params_without_list(self):
        cpage = base.ImageContactPage(page_url=self.IMAGE_URL)
        assert_equals(len(cpage.image_urls), 0)
