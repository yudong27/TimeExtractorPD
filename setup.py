# -*- coding=utf-8 -*-
"""
# library: pednlp
# author: yudong27
# license: Apache License 2.0
# Email: yuu1010@qq.com
# github: https://github.com/yudong27/TimeExtractorPD
# description: Preprocessing & Parsing tool for Chinese NLP
"""

import os
import re
from setuptools import setup, find_packages


DIR_PATH = os.path.dirname(os.path.abspath(__file__))
LONG_DOC = '''
==================================== JioNLP ====================================

中文 NLP 文本预处理与解析工具包，完成 NLP 模型训练前后的预处理与解析，如文本数据增强、
文本清洗、特定信息抽取、数据集概况分析、模型加速、相关模型任务 baseline、各类词典等。

# 安装：
    $ pip install pednlp

# 导入：
    >>> import pednlp

'''
__version__ = ''

with open(os.path.join(DIR_PATH, 'README.md'),
          'r', encoding='utf-8') as f:
    readme_lines = f.readlines()
    version_pattern = re.compile('badge/version-(\d\.\d+\.\d+)-')
    for line in readme_lines:
        result = version_pattern.search(line)
        if result is not None:
            __version__ = result.group(1)

    LONG_DOC = '\n'.join(readme_lines)

__name__ = 'pednlp'
__author__ = "yudong27"
__copyright__ = "Copyright 2022, yudong27"
__credits__ = list()
__license__ = "Apache License 2.0"
__maintainer__ = "yudong27"
__email__ = "yuu1010@qq.com"
__url__ = 'https://github.com/yudong27/TimeExtractorPD'
__description__ = 'Chinese NLP Preprocessing & Parsing'


with open(os.path.join(DIR_PATH, 'requirements.txt'),
          'r', encoding='utf-8') as f:
    requirements = f.readlines()

# delete test module
jionlp_packages = find_packages()
if 'test' in jionlp_packages:
    jionlp_packages.remove('test')

setup(name=__name__,
      version=__version__,
      url=__url__,
      author=__author__,
      author_email=__email__,
      description=__description__,
      long_description=LONG_DOC,
      long_description_content_type='text/markdown',
      license=__license__,
      py_modules=list(),
      packages=jionlp_packages,
      include_package_data=True,
      install_requires=requirements,
      entry_points={
          'console_scripts': [
              'ped_help = pednlp.util:help',
          ]
      },
      test_suite='nose.collector',
      tests_require=['nose'])
