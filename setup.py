from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='quantica',
    version='beta-rc1.0',
    description='A Python framework implemeting Petri Networks',
    url='https://github.com/s4hri/quantica',
    download_url='https://github.com/s4hri/quantica/archive/beta-rc1.0.tar.gz',
    author='Davide De Tommaso',
    author_email='dtmdvd@gmail.com',
    keywords=['petri','networks','python3.8'],
    packages=find_packages(),
    install_requires=["pykron>=0.13"],
    classifiers = [
                    'Programming Language :: Python :: 3.8',
                    'Programming Language :: Python :: 3.9'
    ],
    python_requires='>=3.8',
)
