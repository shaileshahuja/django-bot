from distutils.core import setup

from setuptools import find_packages

setup(
    name='django-bot',
    version='0.0.1',
    packages=find_packages(),
    install_requires=["celery>=4.0", "slackclient==1.0.5", "Django>=1.8"],
    url='https://github.com/shaileshahuja/django-bot',
    license='GNU General Public License v3.0',
    author='shaileshahuja',
    author_email='shailesh.ahuja03@gmail.com',
    description='A django library that makes it easier to develop bots with django',
    classifiers=[
        'Environment :: Bot Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNUv3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
