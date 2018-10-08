import requests
import xml.etree.ElementTree as ET
import json

def GetCBWData( url, cbwmap):
	try:
                req = requests.get(url)
        except Exception:
                print "bad connections"
                return {}
        xmlstr = req.text
        outdict = {}
        for child in ET.fromstring( xmlstr ):
                if child.tag in cbwmap.keys():
                        key = cbwmap[child.tag]
                        try:
                                val = float(child.text)
                        except ValueError:
                                val = -994.0
                        outdict[key] = val

        return outdict



def bokDomeStatus():
	cbwmap = {
        'input1state'   :'dome_open'  ,
        'input2state'   :'dome_closed',
	}

	data = GetCBWData(url="http://140.252.86.113:42744/state.xml", cbwmap=cbwmap )

	return data


def bokAvgOutsideHumidity(minsago=10 ):
	r=requests.get('http://bok.as.arizona.edu:42080/bokdev/bokdev/recent/mins/{}/inhumid'.format(float( minsago ) ) )

	valset = json.loads(r.text)['data']
	
	summer=0
	for timestamp, val in valset:
		
		summer+=float(val)
			
	retn = summer/len(valset)
			

	return retn
