from setuptools import find_packages
from setuptools import setup

import mmttk

setup(
    name='Mikemayer67 Tkinter Widgets',
    version=mmttk.version,
    packages=['mmttk'],
    url='https://github.com/mikemayer67/ttk-widgets',
    license='unlicense',
    author='Michael Mayer',
    author_email='mikemayer67@vmwishes.com',
    description='Collection of custom Tkinter ttk widgets',
    install_requires=['tk'],
)
