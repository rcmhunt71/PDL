import json

from PDL.logger.logger import Logger as Log

log = Log()


class JsonLog(object):

    EXTENSION = 'json'

    # TODO: Add Docstrings

    def __init__(self, image_obj_list, logfile_name):
        self.image_obj_list = image_obj_list
        self.logfile_name = logfile_name

    def write_json(self):
        # Dict (filename: metadata)
        data = dict([(x.filename, x.to_dict()) for x in self.image_obj_list])
        with open(self.logfile_name, "w") as JSON:
            JSON.write(json.dumps(data))
        log.info("Output image info to: {file_spec}".format(file_spec=self.logfile_name))
