"""
 Export multiple ImageData Objects to a single JSON file
"""

import json
from typing import List

from PDL.engine.images.image_info import ImageData
from PDL.logger.logger import Logger as Log

LOG = Log()


class JsonLog:
    """
    This class provides methods to take a python data structure,
    convert it to JSON, and write to file, with it's own logging.

    This is easy to do in code, but rather duplicate the code
    as needed, import and leverage.

    """
    EXTENSION = 'json'

    def __init__(self, image_obj_list: List[ImageData], log_filespec: str) -> None:
        """
        Create the log object

        :param image_obj_list: List of ImageData objects
        :param log_filespec: Filespec (full path/filename) for JSON file

        """
        self.image_obj_list = image_obj_list
        self.logfile_name = log_filespec
        # Convert list of objects into dictionary of dictionaries.
        self.data = {image_obj.filename: image_obj.to_dict() for image_obj
                     in self.image_obj_list}

    def write_json(self) -> None:
        """
        Write image_obj_list to file in JSON format.
        Converts list of objects into a dictionary, where
        the dictionary is {k=image_name: v=image_metadata}

        :return: None

        """
        # Write to file
        with open(self.logfile_name, "w") as json_file:
            json_file.write(json.dumps(self.data))

        # Log action.
        LOG.info(f"Output image info to: {self.logfile_name}")

    def write_to_log(self):
        """
        Rather than write to file, output to the log.

        return: None

        """
        output = json.dumps(self.data)
        for line in output.split('\n'):
            LOG.info(line)
