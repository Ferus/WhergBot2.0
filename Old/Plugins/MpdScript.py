#!/usr/bin/env python
import os
import time

try:
	import mpd
except ImportError:
	print("* [Mpd] Please install python-mpd to use this plugin or remove/rename it. ./Plugins/MpdScript.py")


hostname = "localhost"
port = 6601

client = mpd.MPDClient()
#	client.currentsong() will return a dictionary with song info
#	'album'					# The album the song is from
#	'composer'			# The composer
#	'artist'				# The artist
#	'track'					# The track
#	'title'					# The title
#	'pos'						# The position in the playlist
#	'id'						# The id
#	'last-modified'	# The last time the file was modified
#	'albumartist'		# The album artist
#	'file'					# The full path of the file
#	'time'					# The current time of the song
#	'date'					# Date of the song/album
#	'genre'					# Genre of song
#	'disc'					# Disc number

def mpd_connect():
	try:
		client.connect(hostname,port)
		return True
	except:
		print("* [MPD] Failed to connect to server: {0}:{1}".format(hostname,port))
		return False

def mpd_disconnect():
	try:
		client.close()			# send the close command
		client.disconnect()		# disconnect from the server
	except:
		print("* [MPD] Couldn't disconnect from MPD server.")

def mpdshow_cb(t=True):
	if mpd_connect():
		current_song = client.currentsong()
		current_status = client.status()
		song_filename = os.path.basename(current_song["file"])
		(song_shortname, song_extension) = os.path.splitext(song_filename)
		(song_pos,song_length) = current_status["time"].split(":")

		song_pos = time.strftime('%M:%S', time.gmtime(float(song_pos)))
		song_length = time.strftime('%M:%S', time.gmtime(float(song_length)))

		if t:
			song_s = "({0}/{1})".format(song_pos, song_length)
		else:
			song_s = ''

		mpd_disconnect()
		try:
			return "Now Playing: {0} - {1} - {2} {3}".format(current_song["artist"], current_song["album"], current_song["title"], song_s)
		except:
			return "Now Playing: {0} {1}".format(song_shortname,song_s)
	else:
		print("* [MPD] Couldn't connect to server.")

def mpdprev_cb():
	mpd_connect()
	client.previous()
	mpd_disconnect()
	return mpdshow_cb(t=False)

def mpdnext_cb():
	mpd_connect()
	client.next()
	mpd_disconnect()
	return mpdshow_cb(t=False)

def Music(msg, sock, users, allowed):
	try:
		if msg[4].split()[1:]:
			Text = msg[4].split()[1:]
		else:
			Text = []
		if len(Text) < 1:
			sock.say(msg[3], mpdshow_cb())
		elif Text[0] == "next":
			sock.say(msg[3], mpdnext_cb())
		elif Text[0] == "prev":
			sock.say(msg[3], mpdprev_cb())
	except Exception, e:
		print("* [MPD] Error:\n* [MPD] {0}".format(str(e)))

hooks = {
	'^@mpd': [Music, 0, True],
		}

helpstring = """Gives the owner control over MPD, a music playing daemon.
@mpd next/prev: Changes to next/prev song
@mpd <anythingelse>: Shows currently playing song"""