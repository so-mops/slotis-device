import ephem

def main(val=0):
	kp = ephem.Observer()                  
	kp.lat, kp.lon = '31.9599', '-111.5997'
	hoursToSunset = (kp.next_setting(ephem.Sun())-ephem.now())*24
	hoursToSunset = val
	safe = True
	if hoursToSunset > 12:
		hoursToSunset = abs(hoursToSunset - 24.0)
	if hoursToSunset > 0.25:
		safe = False                                         

	return hoursToSunset, safe

