try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import requests

import PDL.engine.download.pxSite1.parse_page as page
import PDL.engine.images.status as status

from nose.tools import assert_equals

sample_link = r'https://foo.com/clouds.jpeg'
sample_name = r'John Doe'

sample_html_page_format = '''<HTML>
<HEAD>
<TITLE>Your Title Here</TITLE>
</HEAD>
<BODY BGCOLOR="FFFFFF">
<CENTER><IMG "size" : 2048, "url": "{link}", "https_url", ALIGN="BOTTOM", "fullname": "{name}", "_blank"> </CENTER>
<HR>
<a href="http://somegreatsite.com">Link Name</a>
is a link to another nifty site
<H1>This is a Header</H1>
<H2>This is a Medium Header</H2>
Send me mail at <a href="mailto:support@yourcompany.com">
support@yourcompany.com</a>.
<P> This is a new paragraph!
<P> <B>This is a new paragraph!</B>
<BR> <B><I>This is a new sentence without a paragraph break, in bold italics.</I></B>
<HR>
</BODY>
</HTML>
'''

sample_valid_html_page = sample_html_page_format.format(
    link=sample_link, name=sample_name)
sample_invalid_html_page = sample_html_page_format.format(
    link='', name='')

mocked_get_response_proper = requests.Response()
mocked_get_response_proper._content = sample_valid_html_page

mocked_get_no_response = None


class TestParsePage(object):

    DOMAIN_1 = '500px.foo.com'
    DOMAIN_2 = 'web.foo.com'
    DELIM = "sig="
    IMAGE_NAME = 'this_is_my_name'
    DUMMY_URL_FMT = "https://{domain}/help/{delim}{image}"
    DUMMY_URL_1 = DUMMY_URL_FMT.format(
        delim=DELIM, image=IMAGE_NAME, domain=DOMAIN_1)
    DUMMY_URL_2 = DUMMY_URL_FMT.format(
        delim=DELIM, image=IMAGE_NAME, domain=DOMAIN_2)

# ------------ ParseDisplayPage:get_page() ------------

    @patch(
        'PDL.engine.download.pxSite1.parse_page.requests.get',
        return_value=mocked_get_response_proper)
    def test_get_valid_page(self, mock_get):
        valid_page = page.ParseDisplayPage(page_url=self.DUMMY_URL_1)
        page_content = valid_page.get_page()
        assert_equals(
            len(page_content), len(sample_valid_html_page.split('\n')))
        assert_equals(mock_get.call_count, 1)

    @patch(
        'PDL.engine.download.pxSite1.parse_page.requests.get',
        return_value=mocked_get_no_response)
    def test_get_page_with_no_content(self, mock_get):
        valid_page = page.ParseDisplayPage(page_url=self.DUMMY_URL_1)
        page_content = valid_page.get_page()
        print("PAGE CONTENT:\n{0}".format(page_content))
        assert page_content is None
        assert_equals(mock_get.call_count, page.ParseDisplayPage.MAX_ATTEMPTS)

    @patch(
        'PDL.engine.download.pxSite1.parse_page.requests.get',
        side_effect=requests.exceptions.ConnectionError)
    def test_connection_error(self, mock_get):
        # Mocks a connection error. requests.get returns None, so return value
        # should be none, but the mock should have been called MAX_ATTEMPTS
        # times.

        valid_page = page.ParseDisplayPage(page_url=self.DUMMY_URL_1)
        valid_page.RETRY_INTERVAL = 0  # No need to wait, since it is mocked
        page_content = valid_page.get_page()
        print("PAGE CONTENT:\n{0}".format(page_content))
        assert page_content is None
        assert_equals(mock_get.call_count, page.ParseDisplayPage.MAX_ATTEMPTS)

# ------------ ParseDisplayPage:parse_page_for_link() ------------

    def test_parse_page_valid_content_for_link(self):
        valid_page = page.ParseDisplayPage(page_url=self.DUMMY_URL_1)
        valid_page.source = sample_valid_html_page.split('\n')
        link = valid_page.parse_page_for_link()
        assert_equals(link, sample_link)
        assert_equals(valid_page.image_info.dl_status,
                      status.DownloadStatus.NOT_SET)

    def test_parse_page_invalid_content_for_link(self):
        valid_page = page.ParseDisplayPage(page_url=self.DUMMY_URL_1)
        valid_page.source = sample_invalid_html_page.split('\n')
        link = valid_page.parse_page_for_link()
        assert link is None
        assert_equals(valid_page.image_info.dl_status,
                      status.DownloadStatus.ERROR)

# ------------ ParseDisplayPage:translate_unicode_in_link() ------------
    def test_translate_unicode_in_link_with_no_unicode(self):
        link = page.ParseDisplayPage._translate_unicode_in_link(link=sample_link)
        assert_equals(link, sample_link)

    # TODO: Add test for URL with UNICODE (Translate_unicode_in_link)

# ------------ ParseDisplayPage:get_author_name() ------------
    def test_get_valid_page_with_author(self):
        valid_page = page.ParseDisplayPage(page_url=self.DUMMY_URL_1)
        valid_page.source = sample_valid_html_page.split('\n')
        author = valid_page._get_author_name()
        assert_equals(author, sample_name)

    def test_get_valid_page_with_invalid_author(self):
        valid_page = page.ParseDisplayPage(page_url=self.DUMMY_URL_1)
        valid_page.source = sample_invalid_html_page.split('\n')
        author = valid_page._get_author_name()
        assert_equals(author, page.ParseDisplayPage.NOT_FOUND)

# ------------ ParseDisplayPage:get_image_info() ------------
    @patch(
        'PDL.engine.download.pxSite1.parse_page.requests.get',
        return_value=mocked_get_response_proper)
    def test_get_valid_page_info(self, mock_get):
        valid_page = page.ParseDisplayPage(page_url=self.DUMMY_URL_1)
        valid_page.get_image_info()

        assert_equals(
            len(valid_page.source), len(sample_valid_html_page.split('\n')))
        assert_equals(valid_page.image_info.author, sample_name)
        assert_equals(valid_page.image_info.image_url, sample_link)
        assert_equals(valid_page.image_info.page_url, self.DUMMY_URL_1)
        assert_equals(mock_get.call_count, 1)
