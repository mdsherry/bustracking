#!/usr/bin/env python
import sqlite3
conn = sqlite3.connect('busdata.db')
c = conn.cursor()

import csv
c.execute("DROP TABLE triptoroute")
c.execute("CREATE TABLE triptoroute (tripid, routeid)")

for row in csv.DictReader( open('trips.txt', 'rt') ):
	trip_id = int(row['trip_id'])
	route_id = int(row['route_id'])
	c.execute("INSERT INTO triptoroute VALUES (?, ?)", (trip_id, route_id) )

c.execute("DROP TABLE stoptimes")
c.execute("CREATE TABLE stoptimes (arrivaltime, stopid, tripid)")
for row in csv.DictReader( open('stop_times.txt', 'rt') ):
	trip_id = int( row['trip_id'] )
	arrival_time = row['arrival_time']
	stop_id = row['stop_id']
	c.execute("INSERT INTO stoptimes VALUES (?, ?, ?)", (arrival_time, stop_id, trip_id))

c.execute("DROP TABLE stops")
c.execute("CREATE TABLE stops (id, lat, long)")

for row in csv.DictReader( open('stops.txt', 'rt') ):
	stop_id = row['stop_id']
	stop_lat = float(row['stop_lat'])
	stop_lon = float(row['stop_lon'])
	c.execute("INSERT INTO stops VALUES (?, ?, ?)", (stop_id, stop_lat, stop_lon) )
conn.commit()