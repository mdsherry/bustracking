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
parser.add_argument("--nostops", action="store_false", dest="renderStops", help="Show only real-time data")
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


# min_lat = min( x[0] for x in stops.values() )
# max_lat = max( x[0] for x in stops.values() )
# min_lon = min( x[1] for x in stops.values() )
# max_lon = max( x[1] for x in stops.values() )

# Until we've fixed things, we'll hardcode the min/max lat/long to avoid crashes
min_lat, max_lat, min_lon, max_lon = 43.357494, 43.517873, -80.570916, -80.303007

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
speed = 30
while True:
	rttimestamps = []
	lastpos = {}

	for row in c.execute("SELECT DISTINCT time FROM rtentries"):
		rttimestamps.append( row[0] )

	for rttimestamp in rttimestamps:
		t = datetime.fromtimestamp( rttimestamp )
		time = t.minute + (t.hour-5) * 60
		timestamp = times[time]
		if args.renderStops:
			if timestamp in stoptimes:
				for stop, trip_id in stoptimes[timestamp]:
					route = trips[trip_id]
					if route in routes:
						x,y = geomToPixel( *stops[stop] )
						lastpos[trip_id] = x,y
		for bus in c.execute("SELECT tripid, routeid, lat, long FROM rtentries WHERE time = ?", (rttimestamp,) ):
			trip_id, route, lat, lon = bus
			if route not in routes:
				continue
			routeCol = colorForRoute( route )
			
			realx, realy = geomToPixel( lat, lon )

			for d in xrange(-1, 2):
				windowSurfaceObj.set_at( (realx+d,realy-1), routeCol )
				windowSurfaceObj.set_at( (realx+d,realy+1), routeCol )
				windowSurfaceObj.set_at( (realx-1,realy+d), routeCol )
				windowSurfaceObj.set_at( (realx+1,realy+d), routeCol )

			if trip_id in lastpos:
				x,y = lastpos[ trip_id ]
				for d in xrange(-2, 3):

					windowSurfaceObj.set_at( (x+d,y-2), routeCol )
					windowSurfaceObj.set_at( (x+d,y+2), routeCol )
					windowSurfaceObj.set_at( (x-2,y+d), routeCol )
					windowSurfaceObj.set_at( (x+2,y+d), routeCol )

				pygame.draw.line( windowSurfaceObj, routeCol, (x,y), (realx, realy) )						

		tick += 1
		if tick == 1:
			# time += 1
			tick = 0
			pygame.transform.average_surfaces( ( windowSurfaceObj, windowSurfaceObj, windowSurfaceObj, blackSurface), windowSurfaceObj)
			
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.event.post( pygame.event.Event(QUIT) )
				elif event.key == K_s:
					args.renderStops = not args.renderStops
					lastpos = {}
				elif event.key == K_PLUS or event.key == K_EQUALS:
					speed += 5
				elif event.key == K_MINUS:
					speed -= 5
					if speed < 5:
						speed = 5
		pygame.display.update()
		#pygame.image.save( windowSurfaceObj, "{0:05d}.png".format( time ))
		fpsClock.tick(speed)
