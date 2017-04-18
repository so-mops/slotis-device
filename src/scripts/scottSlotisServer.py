#!/usr/bin/python

from server import Server, Client
from scottSock import scottSock
from threading import Thread, Lock
import copy
import time
import json
import os 
import sys
import django                                                                  
from django.utils import timezone                                              
sys.path.append(os.path.abspath("/home/scott/git-clones/slotis-django/slotis"))
os.environ['DJANGO_SETTINGS_MODULE'] = 'slotis.settings'                       
django.setup()                                                                 

from status.models import metone

class LatestThread( Thread ):
	latest = {}
	lock = Lock()
	running = False
	def getlatest(self):
		try:
			s=scottSock('localhost', 5135)
			resp = s.converse('all\n')
		except Exception as err:
			print err
			return 
		lines = resp.split('\n')
		outdict = {}
		errnum = 0
		for line in lines:
			try:
				outlist = line.split(' ')
				key = outlist[0]
				try:
					val = float( line[ len(key): ] )
				except ValueError:
					val = val = line[ len(key): ]
				outdict[key] = val
			except Exception as err:
				outdict['err_'+str(errnum)] = line
				errnum+=1
		with self.lock:
			self.latest.update(outdict)
			self.latest.update({'timestamp': timezone.now().isoformat()})

	def run(self):
		self.running = True
		t0=time.time()
		while self.running:
			#only update every 5 seconds
			if time.time() - t0 > 5.0:
				m=metone()
				if self.latest != {}:
					m.getdata(self.latest)
					m.save()
				self.getlatest()
				t0 = time.time()
			
			time.sleep(0.01)


	


class SlotisClient( Client ):
	
	def handle(self, data):
		self.client.send(json.dumps(LatestThread.latest))


thr=LatestThread()
thr.start()
try:
	s=Server(5000, handler=SlotisClient)
	s.run()
except KeyboardInterrupt:
	print "done"
s.kill()
thr.running=False
thr.join()













