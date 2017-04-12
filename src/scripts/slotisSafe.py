#!/usr/bin/python


#######################################################
# slotisSafe Script
# This script is to run in the background at all times
# and look for unsafe conditions which are enumerated
# below. Upon finding an unsafe condition this script
# will close the Super LOTIS dome. It does not open
# it, it only closes. The rest is left to the perl 
# sripts for automated observing. 
# You will notice that almost every actions is 
# couched in a very open ended except statement. 
# This is somewhat lazy programming but could keep 
# this program from failing on some unkown condition,
# which has been a consistent problem with the perl 
# weather scripts. 
#
#	-Scott Swindell 1/24/2017
#
######################################################

import time
from scottSock import scottSock
import requests
import json
import ephem
from roof import SLroof; myroof = SLroof()
import time
import datetime
from slotis_device import bok
from webWeather import kpDewPoints,  kpWind, fourMeterStatus
# THe webWeather code is a glorified web scraper, with 
# little glory. This should be replace with an actuall weather
# station. Like the super lotis or 90" weather stations. 


#Humidity and wind from the webWeather package seems unreliable at best so 
# we dont trust it. 
#def getHumid():
#	"""Get the himidity from the webWeather package"""
#	try:
#		humid = float( kpDewPoints().getLatest()['2m']['humid'] )
#	except Exception as err:
#		print "{} getHumid error {}, {}".format( time.ctime(), err.message, err.args )
#		humid = 50.0
#	return humid

#def getWind():
#	"Get the Wind From the webWeather package"
#	try:
#		wind = float( kpWind().getLatest()['speed'] )
#	except Exception as err:
#		print "{} getHumid error {}, {}".format( time.ctime(), err.message, err.args )
#		wind = 10
#	print wind
#	return wind
	

	
def mayallIsOpen():
	"""Get the Mayall dome state from the webWeather package"""
	try:
		status = fourMeterStatus().getLatest()['dome_status']
		if status == "CLOSED":
			retn = False
		else:
			retn = True
	except Exception as err:
		retn = None
		print "mayall open", err

	return retn
	

def isRaining(  ):
	"""Get the rain status from the controllino rainbit"""
	try:
		s=scottSock("140.252.86.98", 5750)
	
		response = s.converse("SLOTIS CONTROLLINO1 123 REQUEST RAIN_BIT\n")
		iresp = int(response)
	except Exception as err:
		print "rain bit error", err
		return None

	if iresp == 1:
		return False
	else:
		return True

	return iresp

def bokIsOpen():
	"""Reads the CBW from the bok telescope """
	bokstatus = bok.bokDomeStatus()
	try:
		if bokstatus['dome_closed'] == 1.0:
			return False
		else:
			return True
	except Exception as err:
		print "bok open error", err
		return None
	

	#{'dome_closed': 1.0, 'dome_open': 0.0}

def set_slotis( key, val ):
	"""Set a status in the slotis_status_server"""
	try:
		s=scottSock('localhost', 5135, timeout=0.1)
		resp = s.converse("set {} {}".format(key, val) )
	except Exception as err:
		resp = False
		print 'set sloits err', err

	return resp

def get_slotis( key ):
	"""Get a status from the slotis_status_server"""
	try:
		s=scottSock( 'localhost', 5135, timeout=0.1 )
		resp = s.converse("get {}\n".format(key))
		resp = resp.split()[-1].strip()

	except Exception as err:
		resp = None
		print "get slotis err", err

	return resp

def bokIsTooHumid(  ):
	try:
		h = bok.bokAvgOutsideHumidity()
		if h > 90.0:
			retn = True
		else:
			retn = False
		
	except Exception as err:
		print "bok humid error", err
		return  None
	
	return retn

def isHumanSafe():
	try:
		status = float ( get_slotis('human_safe_to_open') )
		if status == 1.0:
			retn = True
		else:
			retn =  False 

	except Exception as err:
		print 'human safe error', [get_slotis('human_safe_to_open')], err
		retn = None

	return retn

def main():
	
	
	"""The Mainloop. Looks at various conditions and determines weather the
	Super LOTIS dome should be open. If not it issues a close command"""
	l_mayall_is_open = None
	l_bok_is_open = None
	set_slotis("scott_closed_because", 'None')
	while 1:
		t0=time.time()	
		safe = True
		concerns = []

		is_raining = isRaining()
		mayall_is_open = mayallIsOpen()
		bok_is_open = bokIsOpen()
		#bok_is_too_humid = bokIsTooHumid()
		is_human_safe = isHumanSafe()


		instant_status = {
			'isRaining': is_raining, 
			'mayallIsOpen': mayall_is_open,
			'bokIsOpen': bok_is_open,
			#'bokIsTooHumid':bok_is_too_humid,
			'isHumanSafe':is_human_safe
			
		}
		
		#It is raining
		if ( is_raining == True ):
			print "it is raining"
			safe = False
			concerns.append( "rain" )
			

		
		
		#If either dome went from open to closed we should close!
		if mayall_is_open == False and l_mayall_is_open == True:
			print "mayall switched to unsafe"
			safe = False

		if bok_is_open == False and l_bok_is_open == True:
			dt = datetime.datetime.now()
			if dt.hour > 3 and dt.hour< 6:
			
				concerns.append("bok just closed")
				safe = False

		
		#if bok_is_too_humid:
			#print "bok is too humid"
			#safe = False

		if  is_human_safe == False:
			concerns.append( "user set to unsafe" )
			safe = False
		
		if safe:
			# we are just fine continue operating
			set_slotis('scott_safe_to_open', '1.0')
			for n in range( 4 ):
				set_slotis('scott_concern{}'.format(n), "None" )

		else:
			set_slotis('scott_safe_to_open', '0.0')
			#It is unsafe see if we need to close
			try:
				roof_inputs = myroof.getInputs()
			except Exception as err:
				roof_inputs = {"opened": -1, "closed": -1}
				print "roof error", err
			print roof_inputs
			if roof_inputs['opened'] == 1:
				#We are open so lets close
				if roof_inputs['closed'] == 0:
					print "Closing the roof.", concerns
					try:
						set_slotis("scott_closed_because", str(concerns))
						log(str(concerns))
						myroof.closeRoof()

					except Exception as err:
						print "could not close because {}".format(err)
				else:
					# We are open but not all the way, possible moving
					# Lets issue a stop command and then close. 
					print "Stopping then closing the roof."
					try:
						log( str(concerns) )
						myroof.STOP()

						#sleep for 25 seconds to wait for the 
						#roof to close. A terrible way to do this
						#hopefully we can make it more elegant later. 
						time.sleep(5 )
						print "closing roof"
						myroof.closeRoof()
						time.sleep(25)
					except Exception as err:
						print "could not close because {}".format(err)

		#only record the state if we got a good read. 
		if mayall_is_open != None:
			l_mayall_is_open = mayall_is_open
		if bok_is_open != None:
			l_bok_is_open = bok_is_open
		


def log(msg):
	fname='/home/scott/pyslotis.log'
	fd = open(fname, 'a')
	fd.write( "[{}] {}\n".format( time.ctime(), msg ) )

main()
