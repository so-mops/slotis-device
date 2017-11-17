from scottSock import scottSock
import re
import requests

USER = "admin"
PASS = "mtops"

class SLroof_old(  ):
    def __init__( self, ip="140.252.86.97", password="YWRtaW46bXRvcHM=", port=80  ):
        self.password = password
	self.port = port
	self.ip = ip
        self.openRelay = "relay1"
        self.closeRelay = "relay2"
        self.stopRelay = "relay3"
        #self.openRelay = 
        self.pulse = 2
        self.off = 0
        self.on = 1
        self.HTTP = "GET /state.xml?{relay}State={value} HTTP/1.1\nAuthorization: Basic "+password+"\r\n".format(password=password)
	self.HTTPquery = "GET /state.xml HTTP/1.1\nAuthorization: Basic {}\r\n".format(password);

    def converse( self, msg ):
	s=scottSock(self.ip, self.port )
	return s.converse( msg )

    def STOP( self ):

        out = self.HTTP.format( relay=self.stopRelay, value=self.pulse)
        return self.converse( out )


    def START( self ):
        out = self.HTTP.format( relay=self.startRelay, value=self.pulse)
        return self.converse( out )


    def openRoof( self ):
        out = self.HTTP.format( relay=self.openRelay, value=self.pulse)
        print out
        return self.converse( out )

    def closeRoof( self ):
        out = self.HTTP.format( relay=self.closeRelay, value=self.pulse)
	print out
        return self.converse( out )

    def getInputs( self ):
	out = self.HTTPquery	
	xmlre = re.compile("<datavalues>.*<input1state>(\d)<\/input1state>.*<input2state>(\d)<\/input2state>.*<\/datavalues>")
	resp = self.converse(out)
	print resp
	match = xmlre.search(resp)
	try:
		#parse the bits and xor them for clarity
		isClosed, isOpened = int( match.group(1) ), int( match.group(2) )
	except Exception:
		isClosed, isOpened = -1, -1
	return {"opened": isOpened, "closed": isClosed}
	


class SLroof:

	def __init__(self, ip="140.252.86.97", port="80", password=PASS, user=USER):
		self.password = password
		self.user = user
		self.port = port
		self.ip = ip
		self.openRelay = "relay1"
		self.closeRelay = "relay2"
		self.stopRelay = "relay3"
		self.pulse = 2
		self.off = 0
		self.on = 1
		self.urlGetState = "http://"+self.ip+"/state.xml"
		self.urlSetState = "http://"+self.ip+"/state.xml?{relay}State={state}"


	def getInputs( self ):
		rq = requests.get(self.urlGetState, auth=(self.user, self.password))
		return self.parseInputs( rq.text )

	def parseInputs( self, xml ):
		
		xmlre = re.compile("<datavalues>.*<input1state>(\d)<\/input1state>.*<input2state>(\d)<\/input2state>.*<\/datavalues>")
		match = xmlre.search(xml)

		try:
			#parse the bits.
			isClosed, isOpened = int( match.group(1) ), int( match.group(2) )
		except Exception:

			isClosed, isOpened = -1, -1
		return {"opened": isOpened, "closed": isClosed}


	def openRoof( self ):
		URL = self.urlSetState.format( relay=self.openRelay, state=self.pulse )
		rq = requests.get( URL, auth=(self.user, self.password ) )
		return self.parseInputs( rq.text )
		

	def closeRoof( self ):
		URL = self.urlSetState.format( relay=self.closeRelay, state=self.pulse )
		rq = requests.get( URL, auth=(self.user, self.password ) )
		return self.parseInputs( rq.text )

	def STOP( self ):
		URL = self.urlSetState.format( relay=self.stopRelay, state=self.pulse )
		rq = requests.get( URL, auth=(self.user, self.password ) )
		return self.parseInputs( rq.text )


def test():
	r=SLroof()
	return r.getInputs()

