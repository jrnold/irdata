#!/usr/bin/env python
from setuptools import setup

setup(name='irdata',
      version='6.1.0',
      description="International Relations Database",
      author="Jeffrey B. Arnold",
      author_email="jeffrey.arnold@bmail.com",
      package_dir={'irdata': 'irdata'},
      package_data={'irdata': 'data/*'},
      install_requires=['PyYaml >= 3.10',
                        'sqlalchemy >= 0.7.2',
                        'xlrd >= 0.7.1']
     )
