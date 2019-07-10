
import os
import glob
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='writedb_entry_set',
    version='1.0.0',
    description='A Python wrapper for the Artemis writedb_entry script.',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    author='Giles Velarde',
    maintainer='Kevin Pepper',
    maintainer_email='path-help@sanger.ac.uk',
    url='https://github.com/sanger-pathogens/writedb_entry_set',
    scripts=glob.glob('scripts/*'),
    test_suite='nose.collector',
    tests_require=['nose >= 1.3'],
    install_requires=[
        "psycopg2 >= 2.7.6"
    ],
    license='GPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)