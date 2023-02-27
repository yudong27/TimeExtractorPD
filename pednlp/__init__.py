# -*- coding=utf-8 -*-
"""
# library: pednlp
# author: yudong27
# license: Apache License 2.0
# email: yuu1010@qq.com
# github: https://github.com/yudong27/TimeExtractorPD
# description: Preprocessing & Parsing tool for Chinese NLP
"""

__version__ = '0.0.1'


import os
from .timecheck import TimeChecker
time_checker = TimeChecker()
parse = time_checker.parse