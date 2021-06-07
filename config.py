from configparser import ConfigParser
import logging
import sys


class ConfigSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ConfigSingleton, cls).__call__(*args, **kwargs)

            config = ConfigParser()
            config.read('config.ini')

            c = config['CONFIG']

            cls.server = c.get('server', None)
            if cls.server is None or cls.server == '':
                exit(1)

            cls.port = c.get('port', '8443')
            if cls.port == '':
                cls.port = '8443'
            cls.port = int(cls.port)

            cls.test = c.get('test', 'false').lower() == 'true'

        return cls._instances[cls]


def set_logging_configuration(is_client):
    logging_format = '[%(asctime)s] ' + ('CLIENT' if is_client else 'SERVER') + ' - %(levelname)s : %(message)s'
    logging.basicConfig(format=logging_format, level=logging.DEBUG, filename='tls.log', datefmt='%d-%m-%y %H:%M:%S')
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(logging_format, datefmt='%d-%m-%y %H:%M:%S'))
    logging.getLogger().addHandler(handler)


class Config(metaclass=ConfigSingleton):
    pass
