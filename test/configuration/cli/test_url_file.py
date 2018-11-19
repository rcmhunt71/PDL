try:
    # Python 2.7+
    from unittest.mock import patch, create_autospec
except ImportError:
    from mock import patch, create_autospec

import os
import tempfile

import PDL.configuration.cli.url_file as url_file

from nose.tools import assert_equals


class TestUrlFile(object):

    URLS = [
        'https://www.foo.com/url_1',
        'https://www.foo.com/url_2',
        'https://www.foo.com/url_3',
    ]

    FILE_DIR = '/tmp'

    @staticmethod
    def _print_file(filename):
        with open(filename, 'r') as FILE:
            lines = FILE.readlines()

        for line in lines:
            print(line.strip())

    def test_write_file(self):

        filespec = url_file.UrlFile().write_file(
            urls=self.URLS, location=self.FILE_DIR)
        self._print_file(filespec)
        assert os.path.exists(filespec)

        os.remove(filespec)
        assert os.path.exists(filespec) is False

    def test_read_file(self):
        url_filer = url_file.UrlFile()
        filespec = url_filer.write_file(urls=self.URLS, location=self.FILE_DIR)

        url_list = url_filer.read_file(filespec)
        os.remove(filespec)

        print(url_list)
        assert_equals(self.URLS, url_list)
        assert os.path.exists(filespec) is False

    def test_read_non_existent_file(self):
        filespec = r'/tmp/does_not_exist.foo'
        url_list = url_file.UrlFile().read_file(filespec)
        assert_equals(url_list, list())

    def test_read_empty_file(self):
        with tempfile.NamedTemporaryFile(
                mode="w", suffix='jpg', delete=False) as file_obj:
            file_obj.close()
            print("Using an empty file: {0}".format(file_obj.name))
            url_list = url_file.UrlFile().read_file(file_obj.name)

        assert_equals(url_list, list())

# ----------------------------------------------------------------
#       _check_if_location_exists()
# ----------------------------------------------------------------
    def test_check_if_location_exists_but_does_not_exist_no_create(self):
        path_dirs = ['tmp', 'does', 'not', 'exist']
        path = os.path.sep.join(path_dirs)
        create_dir = False

        urlfile = url_file.UrlFile()
        result = urlfile._check_if_location_exists(
            location=path, create_dir=create_dir)
        try:
            os.removedirs(path)
        except OSError:
            pass  # Found a directory that was not empty

        assert result is False
        assert os.path.exists(path) is False

    def test_check_if_location_exists_but_does_not_exist_create(self):
        path_dirs = ['tmp', 'does', 'not', 'exist']
        path = os.path.sep.join(path_dirs)
        create_dir = True

        urlfile = url_file.UrlFile()
        result = urlfile._check_if_location_exists(
            location=path, create_dir=create_dir)
        try:
            os.removedirs(path)
        except OSError:
            pass  # Found a directory that was not empty

        assert result is True
        assert os.path.exists(path) is False

    @patch('PDL.configuration.cli.url_file.os.makedirs',
           side_effect=Exception())
    def test_check_if_location_exists_but_does_not_exist_cannot_create(
            self, makedirs_mock):
        path_dirs = ['tmp', 'does', 'not', 'exist']
        path = os.path.sep.join(path_dirs)
        create_dir = True

        urlfile = url_file.UrlFile()
        result = urlfile._check_if_location_exists(
            location=path, create_dir=create_dir)
        try:
            os.removedirs(path)
        except OSError:
            pass  # Found a directory that was not empty

        assert result is False
        assert makedirs_mock.call_count == 1
        assert os.path.exists(path) is False

    def test_check_if_location_exists_and_does_exist(
            self):
        path_dirs = ['tmp', 'does', 'not', 'exist']
        path = os.path.sep.join(path_dirs)
        create_dir = True
        os.makedirs(path)

        urlfile = url_file.UrlFile()
        result = urlfile._check_if_location_exists(
            location=path, create_dir=create_dir)
        try:
            os.removedirs(path)
        except OSError:
            pass  # Found a directory that was not empty

        assert result is True
        assert os.path.exists(path) is False
