from __future__ import unicode_literals

from django.conf import settings
from django.apps import AppConfig
from pydoc import locate
import logging

logger = logging.getLogger(__name__)


class ConverseConfig(AppConfig):
    name = 'converse'

    def ready(self):
        for mod in settings.ACTION_MODULES:
            logger.debug("Loading action module: {}".format(mod))
            locate(mod)
