#!/usr/bin/python

import sys
import os
import time
from server import Server, Client
from threading import Thread
import django
from django.utils import timezone
sys.path.append(os.path.abspath( "/home/scott/git-clones/slotis-django/slotis" ) )
os.environ['DJANGO_SETTINGS_MODULE'] = 'slotis.settings'
django.setup()


from status.models import metone, boltwood


print metone


while 1:
	try:
		m=metone()
		print m.getdata()
		
		m.save()	
		time.sleep(15)
		b=boltwood()
		print b.getdata()
		b.save()
	except Exception as err:
		print err
	


	time.sleep(5.0)

