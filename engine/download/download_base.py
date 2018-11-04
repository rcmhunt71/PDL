class DownloadImage(object):
    """
    Provided a list of images (or ImageObjects), provide logic for determining
    existence, download, status, location, etc.
    """

    def __init__(self, image_url, dl_dir):
        self.image_url = image_url
        self.dl_dir = dl_dir

    def parse_image_info(self):
        """
        Given the url and dl directory, determine the image name, the final dl
        file spec, and any addition info required for download.

        :return: None

        """
        raise NotImplemented

    def get_image_status(self):
        """
        Determine if image has been downloaded, or already exists. If it does
        exist, don't download again.

        :return: image status

        """
        raise NotImplemented

    def download_image(self):
        """
        Process for downloading image via specified url to the local repository

        :return: status of download.

        """
        raise NotImplemented

# TODO: Add ability to create a queue, and perform multiple, simultaneous DLs
