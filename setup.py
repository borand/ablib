# -*- coding: utf-8 -*-

# based on: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages
import os

the_lib_folder = os.path.dirname(os.path.realpath(__file__))
requirementPath = the_lib_folder + '/requirements.txt'
install_requires = [] # Examples: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ablib',
    version='0.1.0',
    description='My common utility and tools',
    long_description=readme,
    author='Dr. Zej B',
    author_email='borand@borowiec.ca',
    url='https://github.com/borand/ablib',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=install_requires
)
