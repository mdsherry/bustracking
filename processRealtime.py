#!/usr/bin/env python
import time
import urllib2
import json
import collections

VehicleLoc = collections.namedtuple( 'VehicleLoc', 'routeid tripid lat long status')

def retrieveVehicleInfo():
	url = "http://realtimemap.grt.ca/Map/GetVehicles?unique={}&_=1425315125194"
	f = urllib2.urlopen( url.format( time.time() ) )
	return f.read()

def parseVehicleInfo(s):
	data = json.loads( s )
	for row in data:
		yield VehicleLoc( 
			int( row['Trip']['Route']['RouteId']), 
			int( row['Trip']['BlockId']),
			row['Latitude'],
			row['Longitude'],
			int( row['Status'] ))

def main():
	import sqlite3
	conn = sqlite3.connect('busdata.db')
	c = conn.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS rtentries (time, routeid, tripid, lat, long, status)")
	
	vehicles = parseVehicleInfo( retrieveVehicleInfo() )
	curtime = int(time.time())
	c.executemany("INSERT INTO rtentries VALUES (?, ?, ?, ?, ?, ?)", [ (curtime,) + vehicle for vehicle in vehicles] )
	conn.commit()

if __name__ == "__main__":
	# f = open('realtimetest.json','rt')
	# for vehicle in parseVehicleInfo( f.read() ):
	# 	print vehicle
	main()