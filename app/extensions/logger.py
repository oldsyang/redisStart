#!/usr/bin/env python
"""

日志文件配置

# 本来是想 像flask那样把日志对象挂载到app对象上，作者建议直接使用全局对象
https://github.com/tiangolo/fastapi/issues/81#issuecomment-473677039

"""

import os
import time

from loguru import logger

from settings import config

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 定位到log日志文件
log_path = config.LOG_DIR or os.path.join(basedir, 'logs')

if log_path:
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    log_path_error = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}_error.log')

    # 日志简单配置
    logger.add(log_path_error, rotation="12:00", retention="5 days", enqueue=True)

__all__ = ["logger"]
