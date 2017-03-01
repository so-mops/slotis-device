from scottSock import scottSock
import re
class SLroof(  ):
    def __init__( self, ip="140.252.86.97", password="bm9uZTp3ZWJyZWxheQ", port=80  ):
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
        self.HTTP = "GET /state.xml?{relay}State={value} HTTP/1.1\nAuthorization: Basic "+password+"==\r\n\r\n".format(password=password)
	self.HTTPquery = "GET /state.xml HTTP/1.1\nAuthorization: Basic bm9uZTp3ZWJyZWxheQ==\r\n\r\n";

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
        #print out
        return self.converse( out )

    def closeRoof( self ):
        out = self.HTTP.format( relay=self.closeRelay, value=self.pulse)
        return self.converse( out )

    def getInputs( self ):
	out = self.HTTPquery	
	xmlre = re.compile("<datavalues>.*<input1state>(\d)<\/input1state>.*<input2state>(\d)<\/input2state>.*<\/datavalues>")
	resp = self.converse(out)
	match = xmlre.search(resp)
	try:
		#parse the bits and xor them for clarity
		isClosed, isOpened = int( match.group(1) ), int( match.group(2) )
	except Exception:
		isClosed, isOpened = -1, -1
	return {"opened": isOpened, "closed": isClosed}
	


def test():
	r=SLroof()
	return r.getInputs()
	
