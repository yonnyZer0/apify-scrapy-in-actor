__author__ = 'seni'

from colorlog import ColoredFormatter

FRMT = ColoredFormatter(
    "%(log_color)s%(levelname)s: %(reset)s%(asctime_log_color)s%(asctime)s%(reset)s %(message_log_color)s%(message)s",

    # datefmt="%m-%d %H:%M:%S",
    datefmt="%M:%S",
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'black,bg_white',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={
        'message': {
            'DEBUG': 'white',
            'INFO': 'yellow',
            'CRITICAL': 'red,bg_yellow'
        },
        'asctime': {
            'DEBUG':    'blue',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white'
        }
    },
    style='%'
)