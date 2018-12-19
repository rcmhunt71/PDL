import json
import os

import PDL.logger.utils as utils
from PDL.configuration.properties.app_cfg import AppCfgFileSections, AppCfgFileSectionKeys
from PDL.logger.logger import Logger as Log

log = Log()


class JsonLog(object):

    EXTENSION = 'json'

    def __init__(self, image_obj_list, cfg_info, logfile_name):
        self.image_obj_list = image_obj_list
        self.cfg_info = cfg_info
        self.logfile_name = logfile_name
        self.filespec = self.build_json_filespec()

    def build_json_filespec(self):
        location = self.cfg_info.get(AppCfgFileSections.LOGGING,
                                     AppCfgFileSectionKeys.JSON_FILE_DIR)

        # Check if location exists, create if requested
        if not utils.check_if_location_exists(
                location=location, create_dir=True):
            return None

        # Get logging prefix and suffix
        add_ons = [self.cfg_info.get(AppCfgFileSections.LOGGING,
                                     AppCfgFileSectionKeys.PREFIX),
                   self.cfg_info.get(AppCfgFileSections.LOGGING,
                                     AppCfgFileSectionKeys.SUFFIX)]

        # Isolate the timestamp out of the logfile name.
        log_name = self.logfile_name.split(os.path.sep)[-1]
        timestamp = '-'.join(log_name.split('-')[0:-1])
        for update in add_ons:
            if update is not None:
                timestamp.replace(update, '')

        # Build the file name
        filename = "{timestamp}.{ext}".format(timestamp=timestamp,
                                              ext=self.EXTENSION)
        log.debug("Logfile: {log} --> Timestamp = {timestamp}".format(
            timestamp=timestamp, log=self.logfile_name))

        # Build the full file spec
        file_spec = os.path.sep.join([location, filename])
        log.debug('JSON Output File: {json}'.format(json=file_spec))

        return file_spec

    def write_json(self):
        # Dict (filename: metadata)
        data = dict([(x.filename, x.to_dict()) for x in self.image_obj_list])
        with open(self.filespec, "w") as JSON:
            JSON.write(json.dumps(data))
        log.info("Output image info to: {file_spec}".format(file_spec=self.filespec))
