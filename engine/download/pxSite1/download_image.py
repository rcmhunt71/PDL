"""
  Class for downloading the image from the direct URL (contained in the contact sheet
  HTML page). It also scrapes the metadata from the HTML. All image-specific information
  is stored in an instance of the ImageData class.

"""

import datetime
import os
import re
import shutil
import time
from typing import Optional

import requests
import wget

from PDL.engine.download.download_base import DownloadImage
from PDL.engine.images.image_info import ImageData
from PDL.engine.images.status import (
    DownloadStatus as Status,
    ImageDataModificationStatus as ModStatus)
from PDL.logger.logger import Logger

LOG = Logger()


class DownloadPX(DownloadImage):
    """
    Used for DL'ing images from PX site. Scrapes metadata from contact sheet,
    DL's image, uses/generates ImageData object for the image info.
    """

    EXTENSION = 'jpg'  # Default Extension

    URL_KEY = 'sig='   # Key to identify where image name starts

    KILOBYTES = 1024   # in bytes
    MIN_KB = 10        # min file size to not qualify as an image

    RETRY_DELAY = 5    # in seconds
    MAX_ATTEMPTS = 5   # Number of attempts to download

    def __init__(self, image_url: str, dl_dir: str, url_split_token: str = None,
                 image_info: ImageData = None, use_wget: bool = False,
                 test: bool = False) -> None:
        """
        Instantiate an instance of DownloadPX Class

        :param image_url: (str) URL of image to download
        :param dl_dir: (str) Local location where to store downloaded image
        :param url_split_token: (str) Key to determining name of image in URL
        :param image_info: (ImageData) Object used to track image metadata
        :param use_wget: (bool) Use wget instead of requests. Default = False
        :param test: (bool) If testing, don't parse image info

        """
        super(DownloadPX, self).__init__(image_url=image_url, dl_dir=dl_dir)
        self.url_split_token = url_split_token or self.URL_KEY
        self.image_info = image_info or ImageData()
        self.use_wget = use_wget
        self.test = test

        self.id_ = None
        self.image_name = None
        self.dl_file_spec = None
        self._status = Status.NOT_SET

        self.parse_image_info()


    @property
    def status(self) -> str:
        """
        Return page DL status.
        :return: (str) status (See PDL.engine.images.status.DownloadStatus)

        """
        return self._status

    @status.setter
    def status(self, new_status: str) -> None:
        LOG.debug(f"Setting status from '{self._status}' to '{new_status}' for {self.image_url}")
        self._status = new_status
        self.image_info.dl_status = new_status

    def parse_image_info(self) -> None:
        """
        Scrape and store relevant storage information required for the download.
        If testing, may not have metadata, so just skip it. Tests will explicitly
        set the metadata as needed.

        :return: None

        """
        if not self.test:
            self.image_name = self.get_image_name()
            self.id_ = self.image_name.split('.')[0]
            self.dl_file_spec = self._get_file_location(
                image_name=self.image_name, dl_dir=self.dl_dir)

        self.status = Status.PENDING

    def download_image(self) -> str:
        """
        Download the image. If unsuccessful, wait a few seconds and try again,
        up to the maximum number of attempts.

        :return: dl_status (see PDL.engine.images.status),
                 dl_duration (in seconds)

        """
        LOG.debug(f"Image URL: {self.image_url}")
        LOG.debug(f"DL Directory: {self.dl_dir}")

        # Try to download image
        attempts = 0
        LOG.debug(f"Image Status: {self.status}")

        # Set DL and image status
        db_status = ModStatus.MOD_NOT_SET
        exists = False
        if not self.test:
            exists = self._file_exists()
        file_size = 0

        # Start timer
        start_dl = datetime.datetime.now()

        # If image is PENDING and DNE
        if not exists and self.status == Status.PENDING and self.image_name != '':

            # Try to DL
            while (attempts < self.MAX_ATTEMPTS and
                   self.status != Status.DOWNLOADED):
                attempts += 1

                LOG.debug(f"({attempts}/{self.MAX_ATTEMPTS}): Attempting to DL '{self.image_url}'")

                # DL the image
                self.status = self._dl_via_wget() if self.use_wget else self._dl_via_requests()

                # Wait a little bit if the image was not DL'd.
                if self.status != Status.DOWNLOADED:
                    time.sleep(self.RETRY_DELAY)

            # Adjust image status metadata if DL'd
            if self.status == Status.DOWNLOADED:
                db_status = ModStatus.NEW
                if not self.test:
                    file_size = int(os.stat(self.dl_file_spec).st_size)/self.KILOBYTES

        elif exists:
            # Depends if it exists in the DB, but for now, unchanged
            db_status = ModStatus.UNCHANGED

        elif self.image_name != '':
            self.status = Status.ERROR

        # Calculate time to DL
        current_local_time = datetime.datetime.now()
        dl_duration = (current_local_time - start_dl).total_seconds()

        # Update image metadata
        # =============================
        #   Record timestamp in UTC in ISO-8601 format
        current_time_utc = time.mktime(current_local_time.timetuple())
        iso_timestamp = datetime.datetime.utcfromtimestamp(current_time_utc).isoformat()
        self.image_info.downloaded_on = f'{str(iso_timestamp).split(".")[0]}Z'

        self.image_info.download_duration += dl_duration
        self.image_info.mod_status = db_status
        self.image_info.locations.append(self.dl_dir)
        self.image_info.file_size = f"{file_size:0.2f} KB"
        self.image_info.id = self.id_

        # Log status
        LOG.info(f"Downloaded in {dl_duration:0.3f} seconds.")
        LOG.info(f"{self.image_info.page_url} --> {self.status.upper()}")

        return self.status

    def get_image_name(self, image_url: Optional[str] = None, delimiter_key: Optional[str] = None,
                       use_wget: bool = False) -> str:
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

        LOG.debug(f"Image URL: {image_url}")
        if image_url is None:
            msg = 'Image Url is None.'
            self.status = Status.ERROR
            self.image_info.error_info = msg
            LOG.error(msg)
            return ''

        # Build regexp from key
        sig_comp = re.compile(delimiter_key)

        # Check if url has key (try two different ways)
        match = sig_comp.search(image_url)
        if match is not None and not use_wget:
            LOG.debug("Image name found via regex")
            image_name = image_url.split(delimiter_key, 1)[1]

        else:
            LOG.debug("Image name found via wget")
            image_name = wget.filename_from_url(image_url)
            if image_name is not None:
                image_name = image_name.split(delimiter_key, 1)[1]
            LOG.debug(f'Image URL: {image_url}    Image_name: {image_name}   '
                      f'delimiter: {delimiter_key}')

        # Didn't find the url or something bad happened
        if image_name is None:
            msg = f"Unable to get image_name from url: {image_url}"
            self.status = Status.ERROR
            self.image_info.error_info = msg
            LOG.error(msg)

        # Append the extension if it is not present (and image name is not an empty string)
        elif image_name != '' and not image_name.endswith(self.EXTENSION):
            image_name += f'.{self.EXTENSION}'

        LOG.debug(f"Image Name: {image_name}")

        return image_name

    def _get_file_location(self, image_name: Optional[str] = None,
                           dl_dir: Optional[str] = None) -> str:
        """
        Builds download file_spec based on image name and dl_path

        :param image_name: (str) Name of image
        :param dl_dir: (str) Absolute path to download directory

        :return: (str) file_spec of image (dl_path/filename)

        """
        image_name = image_name or self.image_name
        dl_dir = dl_dir or self.dl_dir
        file_spec = None

        # Check data prerequisites are met.
        if image_name is None or dl_dir is None:
            msg = (f'No image name ({image_name}) or base_dir ({dl_dir}) was'
                   ' provided.')
            self.status = Status.ERROR
            self.image_info.error_info = msg
            LOG.error(msg)

        # Build filespec
        else:
            file_spec = os.path.join(dl_dir, image_name)

        return file_spec

    def _file_exists(self) -> bool:
        """
        Check to see if file exists. If it does, set status to prevent DL.

        :return: (bool) Does file exist? T/F

        """
        exists = False

        # Check data prerequisites are met.
        if self.dl_file_spec is None or self.dl_file_spec == '':
            msg = f"No File Location set. Status set to '{self.status}'."
            self.status = Status.ERROR
            self.image_info.error_info = msg
            LOG.error(msg)

        # Check to see if specified file exists, if so, set metadata data
        # and log results
        elif os.path.exists(self.dl_file_spec):
            self.status = Status.EXISTS
            LOG.debug(f"File '{self.dl_file_spec}' already exists. "
                      f"Set status to '{self.status}'")
            exists = True

        # File does not exist. Set metadata and log results
        else:
            LOG.debug(f"File does not exist. {self.dl_file_spec}\n"
                      f"Status set to '{self.status}'")

        # Return results
        return exists

    def _dl_via_wget(self) -> str:
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
        retry_msg = f"Issue Retrieving File. Retrying in {self.RETRY_DELAY} seconds"
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

                    LOG.error(conn_err_msg)
                    time.sleep(self.RETRY_DELAY)

                # Download successful, but check the file size. Error pages will
                # be marked as a successful download, but aren't a success.
                # Delete the file and try again.
                else:
                    if not self.test:
                        file_size = os.path.getsize(filename)

                        if file_size < self.MIN_KB * self.KILOBYTES:
                            self.status = Status.ERROR
                            error_msg = f"Incorrect filesize: {file_size}"
                            self.image_info.error_info = error_msg
                            LOG.warn(error_msg)
                            LOG.warn(retry_msg)
                            os.remove(filename)

                            time.sleep(self.RETRY_DELAY)

            # If out of the attempts loop and unable download: all attempts were
            # connection failures, mark the download as a failure.
            if self.status != Status.DOWNLOADED:
                self.status = Status.ERROR
                self.image_info.error_info = (
                    "All attempts to download were connection failures.")

        # The wget download is not working, so it is an automatic failure.
        else:
            self.status = Status.ERROR
            self.image_info.error_info = "Used wget but wget has SSL issues."

        return self.status

    def _dl_via_requests(self) -> str:
        """
        Download the image via the requests module

        :return: status (refer to PDL.engine.images.status)

        """
        # Download the image
        image = requests.get(self.image_url, stream=True)

        status_msg = (f"File: {self.dl_file_spec} --> "
                      f"DL STATUS CODE: {image.status_code}")

        # If the return code was SUCCESSFUL (200):
        if image.status_code == 200:
            LOG.debug(status_msg)

            # Transfer binary contents to a file (dl_filespec)
            with open(self.dl_file_spec, 'wb') as output_file:
                image.raw.decode_content = True
                shutil.copyfileobj(image.raw, output_file)
                self.status = Status.DOWNLOADED
                self.image_info.error_info = None

        # Any status other than 200 is an error...
        else:
            LOG.error(status_msg)
            self.status = Status.ERROR
            self.image_info.error_info = status_msg

        # Return result of DL
        return self.status
