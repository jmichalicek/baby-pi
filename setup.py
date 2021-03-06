#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.1.0'

if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='baby-pi',
    version=version,
    description="""View emails in development without actually sending them.""",
    long_description=readme + '\n\n' + history,
    author='Justin Michalicek',
    author_email='jmichalicek@gmail.com',
    url='https://github.com/jmichalicek/baby-pi',
    packages=[
        'baby_pi',
    ],
    include_package_data=True,
    install_requires=[],
    license="MIT",
    zip_safe=False,
    keywords=['omxplayer', 'amcrest', 'raspberry pi',],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Kivy',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
