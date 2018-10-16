from ConfigParser import ConfigParser

from PDL.logger.logger import Logger

log = Logger()


class ConfigSectionDoesNotExist(Exception):
    msg_fmt = "Section '{section}' is not defined in '{cfg_file}'"

    def __init__(self, section, cfg_file):
        self.message = self.msg_fmt.format(section=section, cfg_file=cfg_file)


class OptionDoesNotExist(Exception):
    msg_fmt = ("Option '{option}' in section '{section}' "
               "is not defined in '{cfg_file}'")

    def __init__(self, section, option, cfg_file):
        self.message = self.msg_fmt.format(
            section=section, option=option, cfg_file=cfg_file)

class CannotCastValueToType(Exception):
    msg_fmt = ("Option '{option}' in section '{section}' "
               "cannot be cast to '{type_}'in '{cfg_file}'")

    def __init__(self, section, option, cfg_file, type_):
        self.message = self.msg_fmt.format(
            section=section, option=option, cfg_file=cfg_file, type_=type_)


class Config(object):
    def __init__(self, cfg_file):
        self.cfg_file = cfg_file
        self.config = self._read_config()

    def _read_config(self):
        config = ConfigParser()
        config.read(self.cfg_file)
        return config

    def get_sections(self):
        return self.config.sections()

    def get_options(self, section):
        if self.config.has_section(section=section):
            options = self.config.options(section)
            log.debug("Options for {section}:\n{option_list}".format(
                section=section, option_list=["\t{opt}\n".format(opt=opt)
                                              for opt in options]))
            return options
        raise ConfigSectionDoesNotExist(section=section, cfg_file=self.cfg_file)

    def _get_raw_option(self, section, option, api_name):
        if self.config.has_section(section=section):
            if self.config.has_option(section=section, option=option):
                api = getattr(self.config, api_name)
                try:
                    value = api(section=section, option=option)
                except ValueError:
                    type_ = api_name.replace('get_', '')
                    if type_ == '':
                        type_ = 'str'
                    raise CannotCastValueToType(
                        section=section, option=option, cfg_file=self.cfg_file,
                        type_=type_)
                return value
            raise OptionDoesNotExist(
                section=section, option=option, cfg_file=self.cfg_file)
        raise ConfigSectionDoesNotExist(
            section=section, cfg_file=self.cfg_file)

    def get_option(self, section, option):
        api_name = 'get'
        return self._get_raw_option(
            section=section, option=option, api_name=api_name)

    def get_int(self, section, option):
        api_name = 'getint'
        return self._get_raw_option(
            section=section, option=option, api_name=api_name)

    def get_float(self, section, option):
        api_name = 'getfloat'
        return self._get_raw_option(
            section=section, option=option, api_name=api_name)

    def get_boolean(self, section, option):
        api_name = 'getboolean'
        return self._get_raw_option(
            section=section, option=option, api_name=api_name)

    def get_list(self, section, option):
        api_name = 'get'
        list_str = self._get_raw_option(
            section=section, option=option, api_name=api_name)
        return [x.strip() for x in list_str.split(',')]
