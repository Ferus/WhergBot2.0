#!/usr/bin/python2

import mpd
import os
import time

hostname = "localhost"
port = 6601

client = mpd.MPDClient()
#	client.currentsong() will return a dictionary with song info
#	'album'			# The album the song is from
#	'composer'		# The composer
#	'artist'		# The artist
#	'track'			# The track
#	'title'			# The title
#	'pos'			# The position in the playlist
#	'id'			# The id
#	'last-modified'	# The last time the file was modified
#	'albumartist'	# The album artist
#	'file'			# The full path of the file
#	'time'			# The current time of the song
#	'date'			# Date of the song/album
#	'genre'			# Genre of song
#	'disc'			# Disc number

def mpd_connect():
	try:
		client.connect(hostname,port)
		return True
	except:
		print("Failed to connect to MPD: {0}:{1}".format(hostname,port))
		return False

def mpd_disconnect():
	try:
		client.close()			# send the close command
		client.disconnect()		# disconnect from the server
	except:
		print("Couldn't disconnect from MPD server.")
		
def mpdshow_cb():
	if mpd_connect():
		current_song = client.currentsong()
		current_status = client.status()
		song_filename = os.path.basename(current_song["file"])
		(song_shortname, song_extension) = os.path.splitext(song_filename)
		(song_pos,song_length) = current_status["time"].split(":")
	
		song_pos = time.strftime('%M:%S', time.gmtime(float(song_pos)))
		song_length = time.strftime('%M:%S', time.gmtime(float(song_length)))
		mpd_disconnect()
		try:	
			return "Now Playing: {0} - {1} - {2} ({3}/{4})".format(current_song["artist"], current_song["album"], current_song["title"], song_pos,song_length)
		except:
			return "Now Playing: {0} ({1}/{2})".format(song_shortname,song_pos,song_length)
	else:
		print("Couldn't connect to MPD server")

def mpdprev_cb():
	mpd_connect()
	client.previous()				   
	mpd_disconnect() 

def mpdnext_cb():
	mpd_connect()
	client.next()
	mpd_disconnect()

