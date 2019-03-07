"""

   Base class for Downloading Images. (Allows building a class per website, and
   specifying which class to use in the specific config file.

"""

from typing import NoReturn


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
        super(NotImplementedMethod, self).__init__()


class DownloadImage:
    """
    Provided a list of images (or ImageObjects), provide logic for determining
    existence, download, status, location, etc.
    """

    def __init__(self, image_url: str, dl_dir: str) -> None:
        self.image_url = image_url
        self.dl_dir = dl_dir

    def parse_image_info(self) -> NoReturn:
        """
        Given the url and dl directory, determine the image name, the final dl
        file spec, and any addition info required for download.

        :return: No return; raise exception (implementation should return dict)

        """
        raise NotImplementedMethod('parse_image_info')

    def get_image_status(self) -> NoReturn:
        """
        Determine if image has been downloaded, or already exists. If it does
        exist, don't download again.

        :return: No return; raise exception (implementation should return
             <str: DownloadStatus.<str>)

        """
        raise NotImplementedMethod('get_image_status')

    def download_image(self) -> NoReturn:
        """
        Process for downloading image via specified url to the local repository

        :return: No return; raise exception (implementation should return <str>)

        """
        raise NotImplementedMethod('download_image')

# TODO: <CODE> Add ability to create a queue, and perform multiple, simultaneous DLs
