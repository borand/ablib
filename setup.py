# -*- coding: utf-8 -*-

# based on: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages
import ablib
import os

# FROM: https://stackoverflow.com/questions/26900328/install-dependencies-from-setup-py
the_lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = the_lib_folder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ablib',
    version='0.3.0',#ablib.__version__.__version__,
    description='My common utility and tools',
    long_description=readme,
    author='Dr. Zej B',
    author_email='borand@borowiec.ca',
    url='https://github.com/borand/ablib',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=install_requires,
    entry_points={  # points to where the cli is located
        "console_scripts": [
            'ab = ablib.__main__:main'
        ]
    }
)
