import appdirs
import configparser
import logging
import os
import pathlib
from collections import OrderedDict

from chronophore import __title__

logger = logging.getLogger(__name__)


def _load_config(config_file):
    """Load settings from config file and return them as a dict.  If the
    config file is not found, or if it is invalid, create and use a
    default config file.

    :param config_file: `pathlib.Path` object. Path to config file.
    :return: Dictionary of config options.
    """
    logger.debug('Config file: {}'.format(config_file))

    parser = configparser.ConfigParser()
    try:
        with config_file.open('r') as f:
            parser.read_file(f)

    except FileNotFoundError as e:
        logger.warning('Config file not found')
        parser = _use_default(config_file)

    except configparser.ParsingError as e:
        logger.warning('Error in config file: {}'.format(e))
        parser = _use_default(config_file)

    finally:
        try:
            config = _load_options(parser)
        except (configparser.NoOptionError):
            parser = _use_default(config_file)
            config = _load_options(parser)

        logger.debug('Config loaded: {}'.format(config_file))
        return config


def _load_options(parser):
    """Load config options from parser and return them as a dict.

    :param parser: `ConfigParser` object with the values loaded.
    :return: Dictionary of config options.
    """
    config = dict(
        MESSAGE_DURATION=parser.getint('gui', 'message_duration'),
        GUI_WELCOME_LABLE=parser.get('gui', 'gui_welcome_label'),
        FULL_USER_NAMES=parser.getboolean('gui', 'full_user_names'),
        LARGE_FONT_SIZE=parser.getint('gui', 'large_font_size'),
        MEDIUM_FONT_SIZE=parser.getint('gui', 'medium_font_size'),
        SMALL_FONT_SIZE=parser.getint('gui', 'small_font_size'),
        TINY_FONT_SIZE=parser.getint('gui', 'tiny_font_size'),
        MAX_INPUT_LENGTH=parser.getint('gui', 'max_input_length'),
    )
    return config


def _use_default(config_file):
    """Write default values to a config file. If another config file
    already exists, back it up before replacing it with the new file.

    :param config_file: `pathlib.Path` object. Path to config file.
    :return: `ConfigParser` object with the values loaded.
    """
    default_config = OrderedDict((
        (
            'gui',
            OrderedDict(
                (
                    ('message_duration', 5),
                    ('gui_welcome_label', 'Welcome to the STEM Learning Center!'),
                    ('full_user_names', True),
                    ('large_font_size', 30),
                    ('medium_font_size', 18),
                    ('small_font_size', 15),
                    ('tiny_font_size', 10),
                    ('max_input_length', 9),
                )
            ),
        ),
    ))

    parser = configparser.ConfigParser()
    parser.read_dict(default_config)

    if config_file.exists():
        backup = config_file.with_suffix('.bak')
        os.rename(str(config_file), str(backup))
        logger.info('{} moved to {}.'.format(config_file, backup))

    with config_file.open('w') as f:
        parser.write(f)

    logger.info('Default config file created.')

    return parser


CONFIG_FILE = pathlib.Path(appdirs.user_config_dir(__title__), 'config.ini')
os.makedirs(str(CONFIG_FILE.parent), exist_ok=True)
CONFIG = _load_config(CONFIG_FILE)
