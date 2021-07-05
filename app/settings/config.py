import configparser
import os

from .base import *

config_dir = HERE / 'config.ini'
config = configparser.ConfigParser()
config.read(config_dir)

SITE_HOST = os.getenv('SITE_HOST', config.get('global', 'host', fallback=SITE_HOST))
WEB_PORT = int(os.getenv('WEB_PORT', config.get('global', 'web_port', fallback=WEB_PORT)))

REDIS_HOST = os.getenv('REDIS_HOST', config.get('redis', 'redis_host', fallback='localhost'))
REDIS_PORT = os.getenv('REDIS_PORT', config.get('redis', 'redis_port', fallback=6379))
REDIS_PWD = os.getenv('REDIS_PWD', config.get('redis', 'REDIS_PWD', fallback=''))
REDIS_DB = os.getenv('REDIS_DB', config.get('redis', 'REDIS_DB', fallback=0))
REDIS_ENCODING = os.getenv('REDIS_ENCODING', config.get('redis', 'REDIS_ENCODING', fallback='utf-8'))
REDIS_SENTINELS = os.getenv('REDIS_SENTINELS', config.get('redis', 'SENTINEL_HOST', fallback=''))
REDIS_SENTINEL_PWD = os.getenv('REDIS_SENTINEL_PWD', config.get('redis', 'SENTINEL_PWD', fallback=6379))
REDIS_MASTER = os.getenv('REDIS_MASTER', config.get('redis', 'master', fallback='mymaster'))
REDIS_MASTER_PWD = os.getenv('REDIS_MASTER_PWD', config.get('redis', 'master_pwd', fallback=''))

REDIS_URL = f"redis://:{REDIS_PWD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}?encoding={REDIS_ENCODING}"

DB_HOST = os.getenv('DB_HOST', config.get('database', 'host', fallback='localhost'))
DB_USERNAME = os.getenv('DB_USERNAME', config.get('database', 'username', fallback=''))
DB_PWD = os.getenv('DB_PWD', config.get('database', 'password', fallback=''))
DB_PORT = os.getenv('DB_PORT', config.get('database', 'port', fallback=3306))
DB_NAME = os.getenv('DB_NAME', config.get('database', 'db', fallback=''))
DB_CHARSET = os.getenv('DB_CHARSET', config.get('database', 'charset', fallback='ut8mb4'))
DB_TABLE_PREFIX = os.getenv('DB_TABLE_PREFIX', config.get('database', 'prefix', fallback=''))
DB_URL = f'mysql+pymysql://{DB_USERNAME}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset={DB_CHARSET}'

if os.path.isfile(HERE / 'settings/private.py'):
    from .private import *

    REDIS_URL = f"redis://:{REDIS_PWD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}?encoding={REDIS_ENCODING}"
    DB_URL = f'mysql+pymysql://{DB_USERNAME}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset={DB_CHARSET}'

try:
    if REDIS_SENTINELS:
        if isinstance(REDIS_SENTINELS, str):
            REDIS_SENTINELS = REDIS_SENTINELS.split(",")
            REDIS_SENTINELS = [i.split(":") for i in REDIS_SENTINELS]
    else:
        REDIS_SENTINELS = []
except:
    REDIS_SENTINELS = []
