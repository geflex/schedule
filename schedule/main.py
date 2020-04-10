import os
import logging

import bottex
from bottex.views import views
from bottex.utils import i18n

import loggers
from drivers.vk import VkDriver
from views import StartView


def run_app():
    i18n.localedir = os.path.join(os.path.dirname(__file__), 'locale')
    i18n.add_locales('be', 'en', 'ru')
    views.viewnames.default_view = StartView

    vkdriver = VkDriver('drivers/vkdriver.json')
    # socketdriver = SocketDriver('localhost', 8888)
    bottex.run([vkdriver], restart_on_error=True)


if __name__ == '__main__':
    loggers.setup_logging(logging.DEBUG)
    run_app()
    pass
