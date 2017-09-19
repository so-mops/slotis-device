from scottSock import scottSock
import json



class Boltwood:
	def __init__(self, ip="140.252.86.86", port=30000):
		self.ip = ip
		self.port = port

	def getdata(self):
		try:
			s = scottSock(self.ip, self.port)
			data = s.converse("\n")
			jdata = json.loads(data)
			jdata["roofCloseRequested"] = int(jdata["roofCloseRequested"])
			s.close()
		except Exception as err:
			jdata = {}
			jdata["error"] = err
			jdata["roofCloseRequested"] = 1
			
		
		return jdata


	def getdata2(self):
		"""Threshold for dayCond is too high so we figure it out here"""
		try:
			s = scottSock(self.ip, self.port)
			data = s.converse("\n")
			jdata = json.loads(data)
			jdata["roofCloseRequested"] = 0

			if int( jdata["daylightADC"]) > 750:
				jdata["roofCloseRequested"] = 1
			
			elif int( jdata["cloudCond"] ) > 2:
				jdata["roofCloseRequested"] = 1
			
			s.close()
		except Exception as err:
			print err
			jdata = {}
			jdata["error"] = err
			jdata["roofCloseRequested"] = 1
			
		
		return jdata

	def isSafe(self):
		jdata = self.getdata()
		
		if jdata["roofCloseRequested"] == 1:
			return 0
		else:
			return 1

			
		

			
			
		
