import logging
import sys
import time
import traceback


def error_formatter(e):
    _, _, tb = sys.exc_info()
    s = traceback.format_exc()
    return '\n' + ''.join(s)


def on_error(e):
    s = error_formatter(e)
    logging.critical(s)
    # reload_all_modules()
    time.sleep(0.3)


def err_safe_run(func, err_handler):
    while True:
        try:
            func()
        except Exception as e:
            err_handler(e)
