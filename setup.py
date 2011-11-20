#!/usr/bin/python
# -*- coding:utf8 -*-

from distutils.core import setup
from glob import glob

setup(name = 'tweets2pdf',
      version = "0.2.0",
      description = 'Backup your tweets into FANTANSTIC pdf',
      author = 'Levin',
      author_email = 'levin108@gmail.com',
      license = 'GPLv2',
      url = "http://code.google.com/p/tweets2pdf",
      download_url = "http://code.google.com/p/tweets2pdf/downloads/list",
      platforms = ['Linux'],
      requires = ['reportlab'],
      scripts = ['scripts/tweets2pdf'],
      packages = ['tweets2pdf'],
      data_files = [
          ('share/pixmaps', ['tweets2pdf.png'])
          ]
      )
