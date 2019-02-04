import json

from PDL.logger.logger import Logger as Log

log = Log()


class JsonLog(object):
    """
    This class provides methods to take a python data structure,
    convert it to JSON, and write to file, with it's own logging.

    This is easy to do in code, but rather duplicate the code
    as needed, import and leverage.

    """
    EXTENSION = 'json'

    def __init__(self, image_obj_list, log_filespec):
        """
        Create the log object

        :param image_obj_list: List of ImageData objects
        :param log_filespec: Filespec (full path/filename) for JSON file

        """
        self.image_obj_list = image_obj_list
        self.logfile_name = log_filespec

    def write_json(self):
        """
        Write image_obj_list to file in JSON format.
        Converts list of objects into a dictionary, where
        the dictionary is {k=image_name: v=image_metadata}

        :return: None

        """

        # Convert list of objects into dictionary of dictionaries.
        data = dict([(x.filename, x.to_dict()) for x in self.image_obj_list])

        # Write to file
        with open(self.logfile_name, "w") as JSON:
            JSON.write(json.dumps(data))

        # Log action.
        log.info(f"Output image info to: {self.logfile_name}")
