#!/usr/bin/python
from datetime import datetime, timedelta
import argparse
from collections import defaultdict
import sqlite3
conn = sqlite3.connect('busdata.db')
c = conn.cursor()

def minuteToTimestamp(t):
	return "{0:02d}:{1:02d}:00".format( 5 + (t/60), t % 60)


times = [minuteToTimestamp(t) for t in xrange( 2000 )]
import csv

trips = {}
for row in c.execute('SELECT tripid, routeid FROM triptoroute'):
	trips[ row[0] ] = row[1]

parser = argparse.ArgumentParser(description="Draw pretty pictures of busses moving about")
parser.add_argument("-r", "--route", type=int, action='append', help="Numbers of routes to show")
parser.add_argument("-x", "--exclude", type=int, action='append', help="Numbers of routes to hide")

args = parser.parse_args()
if args.route:
	routes = set( args.route )
else:
	routes = set( trips.values() )

if args.exclude:
	routes -= set( args.exclude )

trips = dict( (k,v) for (k,v) in trips.items() if v in routes )

stoptimes = defaultdict(list)
valid_stops = set()
for row in c.execute("SELECT arrivaltime, tripid, stopid FROM stoptimes"):
	trip_id = row[1]
	if trip_id in trips:
		stoptimes[row[0]].append( (row[2], trip_id) )
		valid_stops.add( row[2] )

stops = {}
for row in c.execute("SELECT id, lat, long FROM stops"):
	if row[0] in valid_stops:
		stops[row[0] ] = row[1], row[2]
print end - start


min_lat = min( x[0] for x in stops.values() )
max_lat = max( x[0] for x in stops.values() )
min_lon = min( x[1] for x in stops.values() )
max_lon = max( x[1] for x in stops.values() )


height_km, width_km = (max_lat - min_lat) *  111, (max_lon - min_lon) * 78
width_px = int( width_km * 30 )
height_px = int( height_km * 30 )

def geomToPixel( lat, lon ):
	return int((lon - min_lon) / (max_lon - min_lon) * width_px), height_px - int((lat - min_lat) / (max_lat - min_lat) * height_px)


print min_lat, max_lat, min_lon, max_lon
print width_px, height_px
print 
import hashlib


import sys, pygame
from pygame.locals import *

pygame.init()
fpsClock = pygame.time.Clock()
windowSurfaceObj = pygame.display.set_mode((width_px,height_px))
blackColor = pygame.Color(0,0,0)
redColor = pygame.Color(255,0,0)
windowSurfaceObj.fill( blackColor )

colorsForRoute = {}
for route in set(trips.values()):
	r,g,b = map(ord, hashlib.md5(str(route)).digest()[:3])
	scale = max(r,g,b)
	if scale == 0:
		r,g,b = 255,255,255
	else:
		scale = 255.0/scale
		r,g,b = int(r * scale), int(b * scale), int(g * scale)

	colorsForRoute[route] = pygame.Color( r,g,b )
def colorForRoute( routeId ):
	return colorsForRoute[routeId]

blackSurface = pygame.Surface( (width_px,height_px) )
blackSurface.fill(blackColor)
blackSurface = pygame.image.load('map.png')
time = 0
tick = 0
while True:
	timestamp = times[time]
	if timestamp in stoptimes:
		for stop, trip_id in stoptimes[timestamp]:
			route = trips[trip_id]
			if route in routes:
				x,y = geomToPixel( *stops[stop] )
				windowSurfaceObj.set_at( (x,y), colorForRoute( route ) )
				windowSurfaceObj.set_at( (x,y+1), colorForRoute( route ) )
				windowSurfaceObj.set_at( (x+1,y), colorForRoute( route ) )
				windowSurfaceObj.set_at( (x+1,y+1), colorForRoute( route ) )
	tick += 1
	if tick == 2:
		time += 1
		tick = 0
		pygame.transform.average_surfaces( ( windowSurfaceObj, windowSurfaceObj, windowSurfaceObj, blackSurface), windowSurfaceObj)
		
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		elif event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				pygame.event.post( pygame.event.Event(QUIT) )
	pygame.display.update()
	#pygame.image.save( windowSurfaceObj, "{0:05d}.png".format( time ))
	fpsClock.tick(30)
