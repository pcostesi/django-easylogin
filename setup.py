#!/usr/bin/env python

from distutils.core import setup

setup(
    name='django-easylogin',
    version='0.0.2a',
    author='pcostesi',
    author_email='pcostesi@ieee.org',
    packages=['easylogin'],
    url='https://github.com/pcostesi/django-easylogin',
    license='BSD licence, see LICENCE.md',
    description=('Easily login to a django app using a '
        'mobile device (phone, tablet)'),
    long_description=open('README.md').read()[:-1],
    zip_safe=False,
    install_requires=['qrcode', 'django', 'PIL'],
)
