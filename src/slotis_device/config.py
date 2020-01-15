import os
import json

CONFIGDIR = "/home/scott/.mtnops"
CONFIGNAME = "slotis_dev.json"

class config(object):

	def __init__( self ):
		self.fname = os.path.join(CONFIGDIR, CONFIGNAME)
		if os.path.exists(self.fname):
			self.config = json.load( open( self.fname ) )
		else:
			self.config = {
				"thresholds": {
					"boltwood": {
						"daylightADC" : 750,
						
						"skyMinusAmbientTemperature" : -30 ,
						"windSpeed" : 35 ,
						"relativeHumidityPercentage" : 80 ,
					}
					
				}
				
			}
			with open(self.fname, 'w') as fd:
				json.dump( self.config, fd )
			


	def __getitem__(self, key):

		return self.config[key]
