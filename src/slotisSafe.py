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

from roof import SLroof; myroof = SLroof()

from webWeather import kpDewPoints,  kpWind, fourMeterStatus
# THe webWeather code is a glorified web scraper, with 
# little glory. This should be replace with an actuall weather
# station. Like the super lotis or 90" weather stations. 

def getHumid():
	"""Get the himidity from the webWeather package"""
	try:
		humid = float( kpDewPoints().getLatest()['2m']['humid'] )
	except Exception:
		humid = 100.0
	return humid

def getWind():
	"Get the Wind From the webWeather package"
	try:
		wind = float( kpWind().getLatest()['speed'] )
	except Exception as err:
		wind = 20
	return wind
	
	
def mayallIsOpen():
	"""Get the Mayall dome state from the webWeather package"""
	try:
		status = fourMeterStatus().getLatest()['dome_status']
		if status == "CLOSED":
			retn = 0
		else:
			retn = 1
	except Exception as err:
		retn = 0

	return retn
	

def isRaining(  ):
	"""Get the rain status from the controllino rainbit"""
	try:
		s=scottSock("140.252.86.98", 5750)
	
		response = s.converse("SLOTIS CONTROLLINO1 123 REQUEST RAIN_BIT\n")
		iresp = int(response)
	except Exception as err:
		#can't read the rainbit so set the bit to low (raining)
		iresp = 0
	if iresp == 1:
		return False
	else:
		return True

	return iresp

def set_slotis( key, val ):
	"""Set a status in the slotis_status_server"""
	try:
		s=scottSock('localhost', 5135)
		resp = s.converse("set {} {}".format(key, val) )
	except Exception as err:
		resp = False

	return resp

def get_slotis( key ):
	"""Get a status from the slotis_status_server"""
	try:
		s=scottSock('localhost', 5135)
		resp = s.converse("get {}\n".format(key))
	except Exception as err:
		resp = False

	print resp

def main():
	"""The Mainloop. Looks at various conditions and determines weather the
	Super LOTIS dome should be open. If not it issues a close command"""
	rhs = []
	winds = []

	while 1:
		if len(rhs) > 10:
			rhs.pop(0)
		if len( winds ) > 10:
			winds.pop(0)

		rhs.append( getHumid() )
		winds.append( getWind() )

		safe = True
		concerns = []
		
		#the average humidity is above 85%
		if( sum(rhs)/len(rhs) > 85 ):
			safe = False
			concerns.append("humidity")

		#The average wind speed is above 20MPH
		if ( sum(winds)/len(winds) > 20 ):
			safe = False
			concerns.append("wind")

		#It is raining
		if ( isRaining() ):
			safe = False
			concerns.append( "rain" )

		#The mayall is closed
		if ( mayallIsOpen() == False ):
			safe = False
			concerns.append("Mayall")

		if safe:
			# we are just fine continue operating
			set_slotis('ops_safe_to_open', '1.0')
			for n in range( 4 ):
				set_slotis('scott_concern{}'.format(n), "None" )

			
		else:
			#It is unsafe see if we need to close
			try:
				roof_inputs = myroof.getInputs()
			except Exception as err:
				roof_inputs = {"opened": -1, "closed": -1}
			print roof_inputs
			if roof_inputs['opened'] == 1:
				#We are open so lets close
				if roof_inputs['closed'] == 0:
					print "Closing the roof."
					try:
						myroof.closeRoof()
					except Exception as err:
						print "could not close because {}".format(err)
				else:
					# We are open but not all the way, possible moving
					# Lets issue a stop command and then close. 
					print "Stopping then closing the roof."
					try:
						myroof.STOP()
						time.sleep(5)
						myroof.closeRoof()
					except Exception as err:
						print "could not close because {}".format(err)

					
			set_slotis('ops_safe_to_open', '0.0') 

		
		for n in range( len( concerns ) ):
			
			set_slotis('scott_concern{}'.format(n), concerns[n] )

		time.sleep(1.0)


main()
