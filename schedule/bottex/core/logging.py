import logging


logger = logging.getLogger('bottex')
bottex_logger = logger


def setup_handler(handler, minn, maxx, only):
    start, stop = 0, 9999
    if minn:
        start = minn
    if maxx:
        stop = maxx
    lst = range(start, stop)
    if only:
        if isinstance(only, int):
            lst = range(only, only+1)
        else:
            lst = only

    def filt(record):
        return record.levelno in lst
    handler.addFilter(filt)


def add_handler(file_or_stream, min=None, max=None, only=None):
    if isinstance(file_or_stream, str):
        handler = logging.FileHandler(file_or_stream, encoding='utf-8')
    else:
        handler = logging.StreamHandler(file_or_stream)
    setup_handler(handler, min, max, only)
    logger.addHandler(handler)


def add_splitted(low_level_stream, hi_level_stream, min2=logging.ERROR):
    add_handler(low_level_stream, max=min2)
    add_handler(hi_level_stream, min=min2)


def set_default_format():
    set_format(logging.BASIC_FORMAT)


def set_level(lvl):
    logger.setLevel(lvl)


def set_format(fmt=None, datefmt=None, style='%'):
    formatter = logging.Formatter(fmt, datefmt, style)
    for handler in logger.handlers:
        handler.setFormatter(formatter)


def get_logger(name):
    return logger.getChild(name)
