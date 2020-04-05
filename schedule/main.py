import os
import logging

import bottex
from bottex.views import views
from bottex.core import i18n

import loggers
from drivers.vk import VkDriver
from views import StartView


def run_app():
    app_name = 'bntu_schedule'
    i18n.localedir = os.path.join(os.path.dirname(__file__), 'locale')
    i18n.add_locales('be', 'en', 'ru')
    views.viewnames.default_view = StartView

    vkdriver = VkDriver(app_name, 'drivers/vkdriver.json')
    # socketdriver = SocketDriver(app_name, 'localhost', 8888)
    bottex.run([vkdriver], restart_on_error=True)


if __name__ == '__main__':
    loggers.setup_logging(logging.DEBUG)
    run_app()
    pass
