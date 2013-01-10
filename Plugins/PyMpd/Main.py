#!/usr/bin/env python
import os
import time

import logging
logger = logging.getLogger("PyMPD")

try:
	import mpd
	IMPORT_OK = True
except ImportError:
	logger.warning("* [Mpd] Please install python-mpd to use this plugin or remove /Plugins/PyMpd")
	IMPORT_OK = False

from .Settings import Settings

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
	host, port = (Settings.get("host"), Settings.get("port"))
	try:
		client.connect(host, port)
		return True
	except Exception as e:
		print(repr(e))
		logger.exception("Failed to connect to server: {0}:{1}".format(host,port))
		return False

def mpd_disconnect():
	try:
		client.close()
		client.disconnect()
	except Exception as e:
		print(repr(e))
		logger.exception("Couldn't disconnect from MPD server.")

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
		except Exception as e:
			logger.warning("Exception caught, specify the type.")
			return "Now Playing: {0} {1}".format(song_shortname,song_s)
	else:
		print("* [MPD] Couldn't connect to server.")
		return "Couldn't connect to mpd server."

def mpdprev_cb():
	mpd_connect()
	client.previous()
	mpd_disconnect()
	return mpdshow_cb(t=False)

def mpdnext_cb():
	mpd_connect()
	next(client)
	mpd_disconnect()
	return mpdshow_cb(t=False)

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Music(self, data):
		if IMPORT_OK == False:
			return None
		if data[0] not in Settings.get('allowedusers'):
			return None

		try:
			action = data[4]
		except IndexError:
			self.IRC.say(data[2], mpdshow_cb())
			return None
		if action == 'next':
			mpdnext_cb()
		elif action == 'prev':
			mpdprev_cb()

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__, {'^@mpd(?: \W)?$': self.Music})

	def Unload(self):
		pass
	def Reload(self):
		pass
