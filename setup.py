#!/usr/bin/env python
from setuptools import setup

import os.path as op
CURRENT_DIR = op.dirname(__file__)

version = open(op.join(CURRENT_DIR, 'cloudy_helpers', 'VERSION.txt')).read().strip()

requirements = open(op.join(CURRENT_DIR, 'requirements.txt')).read()

setup(
    name='cloudy_helpers',
    packages=['cloudy_helpers'],

    author='Stupeflix',
    author_email='contact@stupeflix.com',
    description='Cloudy helpers',
    license='MIT',
    keywords='',
    url='https://github.com/Stupeflix/cloudy_helpers',

    version=version,
    include_package_data=True,
    zip_safe=False,
    install_requires=[line for line in requirements.splitlines() if line and not line.startswith("--")],
)
