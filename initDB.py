#!/usr/bin/env python
import sqlite3
import os
import sys

if os.path.exists( 'busdata.db' ) and '--force' not in sys.argv:
	sys.stderr.write("Database already exists; won't overwrite. Call {} --force to override.\n".format( 
		sys.argv[0] ) )
	sys.exit()

conn = sqlite3.connect('busdata.db')

cur = conn.cursor()

cur.execute("CREATE TABLE stops (id, lat, long)")
cur.execute("CREATE TABLE triptoroute (tripid, routeid)")
cur.execute("CREATE TABLE stoptimes (arrivaltime, stopid, tripid)")
conn.commit()