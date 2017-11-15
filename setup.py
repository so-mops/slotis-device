#!/usr/bin/env python

#this is the setup file

from distutils.core import setup
import os

setup(
      name='slotis-weather',
      version='1.0',
      description='A web scraper to get KPNO weather to slotis (not a great idea)',
      author='Scott Swindell',
      author_email='scottswindell@email.arizona.edu',
	  py_modules = ['slotis_device/roof'],
	  packages = ['slotis_device'],
	  package_dir = {'':'src'},
	  scripts = [
		'src/scripts/slotisSafe.py',
		'src/scripts/scottSlotisServer.py',
		],
     )
