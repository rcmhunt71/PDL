class NotImplementedMethod(Exception):
    """
    Needed to implement a "dumb" class so that nose could test DownloadImage
    The 'NotImplemented' exception does not seem to have a __name__ element,
    so nose throws an AttributeError when the exception is raised. By defining
    a specific exception, the __name__ attribute is present. Go figure.
    """

    msg = "Method: {0} not implemented."

    def __init__(self, routine):
        self.message = self.msg.format(routine)


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
        raise NotImplementedMethod('parse_image_info')

    def get_image_status(self):
        """
        Determine if image has been downloaded, or already exists. If it does
        exist, don't download again.

        :return: image status

        """
        raise NotImplementedMethod('get_image_status')

    def download_image(self):
        """
        Process for downloading image via specified url to the local repository

        :return: status of download.

        """
        raise NotImplementedMethod('download_image')

# TODO: <CODE> Add ability to create a queue, and perform multiple, simultaneous DLs
