#!/usr/bin/env python
"""

日志文件配置

# 本来是想 像flask那样把日志对象挂载到app对象上，作者建议直接使用全局对象
https://github.com/tiangolo/fastapi/issues/81#issuecomment-473677039

"""

from loguru import logger

__all__ = ["logger"]
