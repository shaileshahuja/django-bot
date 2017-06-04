from distutils.core import setup

from codecs import open
from os import path
from setuptools import find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-bot',
    version='0.2.2',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=["celery>=4.0", "slackclient==1.0.5", "Django>=1.8", "apiai==1.2.3"],
    url='https://github.com/shaileshahuja/django-bot',
    license='GNU General Public License v3.0',
    author='shaileshahuja',
    author_email='shailesh.ahuja03@gmail.com',
    description='A lightweight django framework for bots',
    long_description=long_description,
    classifiers=[
        'Environment :: Other Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries'
    ]
)
