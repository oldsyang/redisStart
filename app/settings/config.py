import configparser
import os

from .base import *

config_dir = HERE / 'config.ini'
config = configparser.ConfigParser()
config.read(config_dir)

SITE_HOST = os.getenv('SITE_HOST', config.get('global', 'host', fallback=SITE_HOST))
WEB_PORT = int(os.getenv('WEB_PORT', config.get('global', 'web_port', fallback=WEB_PORT)))

if os.path.isfile(HERE / 'settings/private.py'):
    from .private import *
