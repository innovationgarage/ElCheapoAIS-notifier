#!/usr/bin/env python

import setuptools

setuptools.setup(name='elcheapoais-notifier',
      version='0.1',
      description='State notifier for embedded systems',
      long_description='State notifier for embedded systems',
      long_description_content_type="text/markdown",
      author='Egil Moeller',
      author_email='egil@innovationgarage.no',
      url='https://github.com/innovationgarage/ElCheapoAIS-notifier',
      packages=setuptools.find_packages(),
      install_requires=[
      ],
      include_package_data=True,
      entry_points='''
      [console_scripts]
      elcheapoais-notifier = elcheapoais_notifier:main
      '''
  )
