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

#from status.models import metone, boltwood
from slotis_device.boltwood import Boltwood as boltwood
class LatestThread( Thread ):
	lock = Lock()
	running = False
	def getlatest(self):
		try:
			s=scottSock('localhost', 5135, timeout=0.25)
			b=boltwood()
			
			boltwood_data = b.getdata()
			for key, val in boltwood_data.iteritems():
				s.converse('set boltwood_{} {}\n'.format(key, val))
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
		if self.latest == None:
			self.latest = {}
		with self.lock:
			self.latest.update(outdict)
			self.latest.update({'timestamp': timezone.now().isoformat()})

	def run(self):
		self.running = True
		t0=time.time()-6.0# run immediately
		self.latest = None
		while self.running:
			#only update every 5 seconds
			
			if time.time() - t0 > 5.0:
				#m=metone()
				if self.latest != None:
					pass
					#m.getdata(self.latest)
					#m.save()
				t0 = time.time()
				self.getlatest()
			time.sleep(0.01)


	


class SlotisClient( Client ):
	
	def handle(self, data):
		self.client.send(json.dumps(thr.latest))


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













