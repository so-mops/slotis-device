from scottSock import scottSock
import json
import pandas as pd
import sqlite3
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Float 
import datetime
import pytz
import json
from config import config as cfg; Config = cfg()

SQLDB = "/home/scott/db/slotis.db"
TBLNM = 'boltwood'
BWIP = "140.252.86.86"
BWPORT = 30000

engine = create_engine( "sqlite:///"+SQLDB )
Base = declarative_base( )


class Boltwood:
	def __init__( self, ip=BWIP, port=BWPORT, sqldb=SQLDB, tblname=TBLNM ):
		self.ip = ip
		self.port = port
		self.datamap = {}
		self.sqldb = sqldb
		self.tblname = tblname

	def getdata(self):
		try:
			s = scottSock(self.ip, self.port, timeout=0.1)
			data = s.converse("\n")
			jdata = json.loads(data)
			jdata["roofCloseRequested"] = int(jdata["roofCloseRequested"])
			s.close()
		except Exception as err:
			jdata = {}
			jdata["error"] = err
			jdata["roofCloseRequested"] = 1
			jdata["timestamp"] = str(pd.Timestamp.now("utc"))
			
		
	
		return jdata

	def to_sql_old(self, data=None):
		
		if data is None:
			data = self.getdata()
		try:
			#conn = sqlite3.connect(self.sqldb)
			engine = create_engine("sqlite:///"+self.sqldb)
			conn = engine.connect()
			pd.DataFrame(data, index=[0]).to_sql(self.tblname, conn, if_exists='append')
			retn = True
		except Exception as err:
			print err
			retn = False

		return retn

	def to_sql( self, data=None ):
		if data is None:
			data = self.getdata()
		try:
			session = BoltwoodSQL.bounded_session()
			session.add(BoltwoodSQL( **data ))
			session.commit()
			session.close()
		except Exception as err:
			
			print( datetime.datetime.now().isoformat(), "Could not write Boltwood to database", err  )

			
	
	def update_status_server(self):
		jdata = self.getdata()
		try:
			for (key, val) in jdata.iteritems():
				soc = scottSock("localhost", 5135)
				out = "set boltwood_{} {}\n".format(key, val)
				soc.send(out)
				soc.close()
		except Exception as err:
			print("Error talking to status server", err)
		return jdata
			

	def getdata2(self):
		"""Threshold for dayCond is too high so we figure it out here"""
		try:
			s = scottSock(self.ip, self.port)
			data = s.converse("\n")
			jdata = json.loads(data)
			jdata["roofCloseRequested"] = 0

			if int( jdata["daylightADC"]) > Config["thresholds"]["boltwood"]["daylightADC"]:
				jdata["roofCloseRequested"] = 1
			

			elif int( jdata["skyMinusAmbientTemperature"] < Config["thresholds"]["boltwood"]["skyMinusAmbientTemperature"] ):
				jdata["roofCloseRequested"] = 1

			elif int( jdata["windSpeed"] > Config["thresholds"]["boltwood"]["windSpeed"] ):
				jdata["roofCloseRequested"] = 1	

			elif int( jdata["relativeHumidityPercentage"] > Config["thresholds"]["boltwood"]["relativeHumidityPercentage"] ):
				jdata["roofCloseRequested"] = 1

			
			s.close()
		except Exception as err:
			print err
			jdata = {}
			jdata["error"] = err
			jdata["roofCloseRequested"] = 1
			
		
		return jdata


	def isSafe( self, update_server=False, log=True ):
		if update_server:
			jdata=self.update_status_server()
		else:
			jdata = self.getdata()
		
		if log:
			self.to_sql(jdata)
		if jdata["roofCloseRequested"] == 1:
			return 0
		else:
			return 1



class BoltwoodSQL(Base):
	__tablename__=TBLNM
	id = Column( Integer, primary_key=True )
	cloudCond = Column( SmallInteger() ) 
	dayCond = Column( SmallInteger() )
	daylightADC = Column( SmallInteger() )
	powerVoltage = Column( Float() )
	rainSensor = Column( Integer() )
	relativeHumidityPercentage = Column( SmallInteger() )
	roofCloseRequested = Column( SmallInteger()  )
	skyMinusAmbientTemperature = Column( Float() )
	timestamp = Column( DateTime() )
	wetSensor = Column( SmallInteger() )
	windSpeed = Column( Float() )

	def __init__(self, **kwargs):
		ts = pytz.UTC.localize( datetime.datetime.strptime(kwargs["timestamp"], "%Y-%m-%dT%H:%M:%SZ") )
		ts = ts.astimezone(pytz.timezone("US/Arizona"))

		kwargs["timestamp"] = ts

		super(BoltwoodSQL, self).__init__(**kwargs)


	def __str__(self):
		return json.dumps( self.dictify(), indent=2
		)
		
	def dictify(self):
		return {
			"cloudCond":self.cloudCond ,
			"dayCond":self.dayCond ,
			"daylightADC":self.daylightADC ,
			"powerVoltage":self.powerVoltage ,
			"rainSensor":self.rainSensor ,
			"relativeHumidityPercentage":self.relativeHumidityPercentage ,
			"roofCloseRequested":self.roofCloseRequested ,
			"skyMinusAmbientTemperature":self.skyMinusAmbientTemperature ,
			"timestamp":str(self.timestamp) ,
			"wetSensor":self.wetSensor ,
			"windSpeed":self.windSpeed ,
			}
	
	@staticmethod
	def bounded_session():
		engine = create_engine( "sqlite:///"+SQLDB )
		session=sessionmaker(bind=engine)()
		return session

	@staticmethod 
	def query():
		session = BoltwoodSQL.bounded_session()
		
		return session.query( BoltwoodSQL )
		
		

	@staticmethod
	def before( dt ):
		session = BoltwoodSQL.bounded_session()
		qr = session.query( BoltwoodSQL ).filter( BoltwoodSQL.timestamp < dt )
		ex = session.bind.execute( qr.selectable )
		data = pd.DataFrame( ex.fetchall() )
		if data.empty:
			return None
		data.columns = [key.replace("boltwood_", '') for key in ex.keys()]
		session.close()
		return data

	@staticmethod
	def after( dt ):
		session = BoltwoodSQL.bounded_session()
		qr = session.query( BoltwoodSQL ).filter( BoltwoodSQL.timestamp > dt )
		ex = session.bind.execute( qr.selectable )
		data = pd.DataFrame( ex.fetchall() )
		if data.empty:
			return None
		data.columns = [key.replace("boltwood_", '') for key in ex.keys()]
		session.close()
		return data

	@staticmethod
	def between(start, end):
		session = BoltwoodSQL.bounded_session()
		qr = session.query( BoltwoodSQL ).filter( BoltwoodSQL.timestamp > start ).filter(BoltwoodSQL.timestamp < end)
		ex = session.bind.execute( qr.selectable )
		data = pd.DataFrame( ex.fetchall() )
		if data.empty:
			return None
		data.columns = [key.replace("boltwood_", '') for key in ex.keys()]
		session.close()
		return data

	@staticmethod
	def recent(minsago=30):
		now=datetime.datetime.now()
		start = now-datetime.timedelta(minutes=minsago)
		print start
		return BoltwoodSQL.between(start, now)


		
def makeDB(sqldb=SQLDB, tblname=TBLNM):
	"""This makes the database it, 
	should only need to be run once"""

	engine = create_engine("sqlite:///"+sqldb)

	session = sessionmaker(bind=engine)()
	Base.metadata.create_all(engine)
	
	
def sql_session(sqldb=SQLDB):
	engine = create_engine("sqlite:///"+SQLDB)
	session = sessionmaker(bind=engine)()

	return session
	
	
	
	
