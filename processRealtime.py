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
import pprint
pp = pprint.PrettyPrinter()

def parseVehicleInfo(s):
	data = json.loads( s )
	for row in data:
		pp.pprint( row )
		yield VehicleLoc( 
			int( row['Trip']['Route']['RouteId']), 
			int( row['Trip']['BlockId']),
			row['Latitude'],
			row['Longitude'],
			int( row['Status'] ))


if __name__ == "__main__":
	f = open('realtimetest.json','rt')
	for vehicle in parseVehicleInfo( f.read() ):
		print vehicle