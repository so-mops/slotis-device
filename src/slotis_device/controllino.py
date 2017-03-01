from scottSock import scottSock


plzip='140.252.86.98'
plzport='5750'


def cmdPLZ( plz_num, state ):
	s=scottSock(plzip, plzport)
	if state in [ 1, True, 'true', 'ON' ]:
		state="ON"
	else:
		state="OFF"
	outstr = "SLOTIS CONTROLLINO1 123 COMMAND PLZ {} ON\n".format( plz_num )
	print outstr
	return s.converse( outstr )


def reqPLZ(plz_num=1, ):
	s=scottSock(plzip, plzport)
	outstr="SLOTIS CONTROLLINO1 123 REQUEST PLZ {} STAT\n".format( plz_num ) 
	print outstr
	return s.converse( outstr )
	




def reqFLOW( subsys='VOLUME' ):
	s=scottSock(plzip, plzport)
	if subsys not in ['BIT', 'VOLUME']:
		raise Exception("subsys argument must be either VOLUME or BIT".format(subsys))
	outstr = "SLOTIS CONTROLLINO1 123 REQUEST CHILLER FLOW_{} \n".format(subsys)

	return s.converse(outstr)
