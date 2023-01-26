from setuptools import find_packages
from setuptools import setup

import mmtk

setup(
    name='mmtk',
    version=mmtk.version,
    packages=['mmtk'],
    url='https://github.com/mikemayer67/mmtk',
    license='unlicense',
    author='Michael Mayer',
    author_email='mikemayer67@vmwishes.com',
    description='Collection of custom Tkinter widgets',
    install_requires=['tk'],
)
