#!venv/bin/python
"""Clase que carga la configuración del proyecto"""

# a simple function to read an array of configuration files into a config object

from os import path

from setuptools import setup, find_packages

import config

here = path.abspath(path.dirname(__file__))

setup(
    name=config.__project,
    version=config.__version,
    description=config.__description,
    author=config.__autor,
    # url='hhtp://joebloggsblog.com',
    packages=find_packages(),  # ['watchDog'],
    # TODO test this mode to install requirement scripts
    install_requires=[i.strip() for i in open(path.join(here, 'requirements.txt')).readlines()],
    # install_requires=[i.strip() for i in open("requirements.txt").readlines()],
    # scripts=['path/to/your/script'],
)
