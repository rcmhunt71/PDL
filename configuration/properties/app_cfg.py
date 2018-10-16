from ConfigParser import ConfigParser, NoSectionError, NoOptionError

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


class AppConfig(ConfigParser):
    def __init__(self, cfg_file):
        ConfigParser.__init__(self)
        self.cfg_file = cfg_file
        self.config = self.read(self.cfg_file)

    def get_options(self, section):
        if self.has_section(section=section):
            options = self.options(section)
            log.debug("Options for {section}:\n{option_list}".format(
                section=section, option_list=["\t{opt}\n".format(opt=opt)
                                              for opt in options]))
            return options
        raise ConfigSectionDoesNotExist(section=section, cfg_file=self.cfg_file)

    def _get_raw_option(self, section, option, api_name):
        if self.has_section(section=section):
            if self.has_option(section=section, option=option):
                api = getattr(self, api_name)
                return api(section=section, option=option)
            raise NoOptionError(section, option)
        raise NoSectionError(section)

    def getlist(self, section, option):
        api_name = 'get'
        list_str = self._get_raw_option(
            section=section, option=option, api_name=api_name)
        return [x.strip() for x in list_str.split(',')]
