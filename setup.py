import unittest
import os
from setuptools import setup
from distutils.core import Command

HERE = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(HERE, "README.rst")

classifiers = [
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Natural Language :: English',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Education',
    'Intended Audience :: Information Technology',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
]

class RunBFITests(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        suite = unittest.TestLoader().discover("bfi/test")
        t = unittest.TextTestRunner(verbosity = 2)
        t.run(suite)

with open(README, 'r') as f:
    long_description = f.read()

setup(
    name='bfi',
    version='0.2.7',
    description=('A reasonably fast optimizing Brainfuck interpreter '
        'in pure python'),
    long_description=long_description,
    url='http://github.com/eriknyquist/bfi',
    author='Erik Nyquist',
    author_email='eknyquist@gmail.com',
    license='Apache 2.0',
    packages=['bfi'],
    scripts=['bin/bfi'],
    classifiers = classifiers,
    cmdclass={'test': RunBFITests},
    include_package_data=True,
    zip_safe=False
)
