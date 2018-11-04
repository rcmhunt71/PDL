class DownloadImages(object):
    """
    Provided a list of images (or ImageObjects), provide logic for determining
    existence, download, status, location, etc.
    """

    def __init__(self, image_list):
        self.image_list = image_list

    def get_image_status(self, image):
        """
        Determine if image has been downloaded, or already exists. If it does
        exist, don't download again.

        :return: image status

        """
        raise NotImplemented

    def download_image(self, url):
        """
        Process for downloading image via specified url to the local repository

        :return: status of download.

        """
        raise NotImplemented

# TODO: Add ability to create a queue, and perform multiple, simultaneous DLs
