import importlib
import logging
import sys


def reload_all_modules():
    root_path = sys.path[0]
    for module in sys.modules.values():
        module_path = getattr(module, '__file__', '')
        if module_path.startswith(root_path):
            importlib.reload(module)
    logging.info('Project modules was reloaded')


def _init_app_modules():
    importlib.import_module('models')
