import os
import re
import shutil
import time

import requests
import wget


from PDL.engine.download.download_base import DownloadImage
from PDL.engine.images.image_info import ImageData
from PDL.engine.images.status import DownloadStatus as Status
from PDL.logger.logger import Logger


log = Logger()

# TODO: <CODE> Need to remove specifics to 500 in this file, and create 500 specific file
#       that passes in the necessary info (or does the URL processing externally


class DownloadPX(DownloadImage):

    EXTENSION = 'jpg'  # Default Extension

    # URL_KEY = 'sig='   # Key to identify where image name starts
    URL_KEY = 'sig%3D'   # Key to identify where image name starts

    KILOBYTES = 1024   # in bytes
    MIN_KB = 10        # min file size to not qualify as an image

    RETRY_DELAY = 5    # in seconds
    MAX_ATTEMPTS = 5   # Number of attempts to download

    def __init__(self, image_url, dl_dir, url_split_token=None, image_info=None,
                 use_wget=False):
        """
        Instantiate an instance of DownloadPX Class

        :param image_url: (str) URL of image to download
        :param dl_dir: (str) Local location where to store downloaded image
        :param url_split_token: (str) Key to determining name of image in URL
        :param image_info: (ImageData) Object used to track image metadata
        :param use_wget: (bool) Use wget instead of requests. Default = False

        """
        super(DownloadPX, self).__init__(image_url=image_url, dl_dir=dl_dir)
        self.url_split_token = url_split_token or self.URL_KEY
        self.image_name = None
        self.dl_file_spec = None
        self.image_info = image_info or ImageData()
        self._status = Status.NOT_SET
        self.use_wget = use_wget
        self.parse_image_info()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        log.debug("Setting status from '{orig}' to '{to}' for {image}".format(
            orig=self._status, to=status, image=self.image_url))
        self._status = status
        self.image_info.dl_status = status

    def parse_image_info(self):
        """
        Get and build all relevant information required for the download.

        :return: None

        """
        self.image_name = self.get_image_name()
        self.dl_file_spec = self._get_file_location(
            image_name=self.image_name, dl_dir=self.dl_dir)
        self.status = Status.PENDING

    def download_image(self):
        """
        Download the image. If unsuccessful, wait a few seconds and try again,
        up to the maximum number of attempts.

        :return: dl_status (see PDL.engine.images.status)

        """
        log.debug("Image URL: {url}".format(url=self.image_url))
        log.debug("DL Directory: {dl_dir}".format(dl_dir=self.dl_dir))

        # Try to download image
        attempts = 0
        status = self.status
        if not self._file_exists() and status == Status.PENDING:
            while (attempts < self.MAX_ATTEMPTS and
                   status != Status.DOWNLOADED):
                attempts += 1

                log.debug("({attempt}/{max}: Attempting to DL '{url}'".format(
                    attempt=attempts, max=self.MAX_ATTEMPTS, url=self.image_url)
                )

                if self.use_wget:
                    status = self._dl_via_wget()
                else:
                    status = self._dl_via_requests()

                if self.status != Status.DOWNLOADED:
                    time.sleep(self.RETRY_DELAY)

        log.info("Image download status for {0}: {1}".format(
            self.image_url, status))
        return status

    def get_image_name(self, image_url=None, delimiter_key=None,
                       use_wget=False):
        """
        Builds image name from URL

        :param image_url: (str) Image URL
        :param delimiter_key: (str) - Token used to determine start of image
                                      name in url
        :param use_wget: (boolean) - For testing purposes or specific need,
                                     force use of wget.

        :return: (str) Name of URL

        """
        image_url = image_url or self.image_url
        delimiter_key = delimiter_key or self.url_split_token

        log.debug("Image URL: {0}".format(image_url))
        if image_url is None:
            log.error('Image Url is None.')
            self.status = Status.ERROR
            return None

        # Build regexp from key
        sig_comp = re.compile(delimiter_key)

        # Check if url has key (try two different ways)

        match = sig_comp.search(image_url)
        if match is not None and not use_wget:
            log.debug("Image name found via regex")
            image_name = image_url.split(delimiter_key)[1]
        else:
            log.debug("Image name found via wget")
            image_name = wget.filename_from_url(image_url)
            if image_name is not None:
                image_name = image_name.strip(delimiter_key)

        # Didn't find the url or something bad happened
        if image_name is None:
            self.status = Status.ERROR
            log.error("Unable to get image_name from url: {url}".format(
                url=image_url))

        # Append the extension
        else:
            image_name += '.{0}'.format(self.EXTENSION)

        log.debug("Image Name: {image_name}".format(image_name=image_name))

        return image_name

    def _get_file_location(self, image_name=None, dl_dir=None):
        """
        Builds download file_spec based on image name and dl_path

        :param image_name: (str) Name of image
        :param dl_dir: (str) Absolute path to download directory

        :return: (str) file_spec of image (dl_path/filename)

        """
        image_name = image_name or self.image_name
        dl_dir = dl_dir or self.dl_dir
        file_spec = None

        if image_name is None or dl_dir is None:
            msg = ('No image name ({image}) or base_dir ({base}) was'
                   ' provided.'.format(image=image_name, base=dl_dir))
            log.error(msg)
            self.status = Status.ERROR
        else:
            file_spec = os.path.join(dl_dir, image_name)

        return file_spec

    def _file_exists(self):
        """
        Check to see if file exists. If it does, set status to prevent DL.

        :return: (bool) Does file exist?

        """
        exists = False

        if self.dl_file_spec is None or self.dl_file_spec == '':
            self.status = Status.ERROR
            log.error("No File Location set. Status set to '{0}'.".format(
                self.status))

        elif os.path.exists(self.dl_file_spec):
            self.status = Status.EXISTS
            log.debug("File '{0}' already exists. Set status to '{1}'".format(
                self.dl_file_spec, self.status))
            exists = True

        else:
            log.debug("File does not exist. {0}\nStatus set to '{1}'".format(
                self.dl_file_spec, self.status))

        return exists

    def _dl_via_wget(self):
        """
        Download the image via wget.

        Currently having issues with certificates. Page changed process, and
        wget cannot validate the certificate. Wget does not have a method to
        prevent certificate validation. (Known issue and request since 2014
        time frame.)
            working = False

        :return: status (refer to PDL.engine.images.status)

        """

        # Messages
        retry_msg = "Issue Retrieving File. Retrying in {0} seconds".format(
            self.RETRY_DELAY)
        conn_err_fmt = ("Attempt {attempts} of {max}: Connection Error --> "
                        "Trying again in {delay} seconds")

        if self.use_wget:
            attempts = 0

            # Download image via wget.download()
            while (attempts < self.MAX_ATTEMPTS and
                   self.status != Status.DOWNLOADED):

                attempts += 1
                try:
                    filename = wget.download(
                        url=self.image_url, out=self.dl_file_spec)
                    self.status = Status.DOWNLOADED

                # Connection failed, wait and try again
                except requests.exceptions.ConnectionError:
                    self.status = Status.PENDING

                    conn_err_msg = conn_err_fmt.format(
                        attempts=attempts, delay=self.RETRY_DELAY,
                        max=self.MAX_ATTEMPTS)

                    log.error(conn_err_msg)
                    time.sleep(self.RETRY_DELAY)

                # Download successful, but check the file size. Error pages will
                # be marked as a successful download, but aren't a success.
                # Delete the file and try again.
                else:
                    file_size = os.path.getsize(filename)

                    if file_size < self.MIN_KB * self.KILOBYTES:
                        self.status = Status.ERROR
                        os.remove(filename)

                        log.warn(retry_msg)
                        time.sleep(self.RETRY_DELAY)

            # If out of the attempts loop and unable download: all attempts were
            # connection failures, mark the download as a failure.
            if self.status != Status.DOWNLOADED:
                self.status = Status.ERROR

        # The wget download is not working, so it is an automatic failure.
        else:
            self.status = Status.ERROR

        return self.status

    def _dl_via_requests(self):
        """
        Download the image via the requests module

        :return: status (refer to PDL.engine.images.status)
        """

        # Download the image
        image = requests.get(self.image_url, stream=True)

        status_msg = "File: {0}\n\tDL STATUS CODE: {1}".format(
                self.dl_file_spec, image.status_code)

        # If the return code was SUCCESSFUL (200):
        if image.status_code == 200:
            log.debug(status_msg)

            # Transfer binary contents to a file (dl_filespec)
            with open(self.dl_file_spec, 'wb') as OUTPUT:
                image.raw.decode_content = True
                shutil.copyfileobj(image.raw, OUTPUT)
                self.status = Status.DOWNLOADED

        # Any status other than 200 is an error...
        else:
            log.error(status_msg)
            self.status = Status.ERROR

        return self.status
