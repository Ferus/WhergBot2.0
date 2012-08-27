# -*- coding: utf-8 -*-
#
# PyBorg: The python AI bot.
#
# Copyright (c) 2000, 2006 Tom Morton, Sebastien Dailly
#
#
# This bot was inspired by the PerlBorg, by Eric Bock.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#        
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# Tom Morton <tom@moretom.net>
# Seb Dailly <seb.dailly@gmail.com>
#

from random import *
import sys
import os
import marshal	# buffered marshal is bloody fast. wish i'd found this before :)
import struct
import time
import re

def filter_message(message, bot):
	"""
	Filter a message body so it is suitable for learning from and
	replying to. This involves removing confusing characters,
	padding ? and ! with ". " so they also terminate lines
	and converting to lower case.
	"""
	# to lowercase
	message = message.lower()
	# remove garbage
	message = re.sub("\"", "", message)
	message = re.sub("<[^<]+?>", "", message)
	message = re.sub("\([^<]+?\)", "", message)
	message = re.sub("\[[^<]+?\]", "", message)
	message = message.replace(";", ",")
	message = message.replace("?", " ? ")
	message = message.replace("!", " ! ")
	message = message.replace(".", " . ")
	message = message.replace(",", " , ")
	message = message.replace("'", " ' ")
	message = message.replace(":", " : ")
	return message

class pyborg(object):
	ver_string = "I am a version 1.1.2 PyBorg, with Seisatsu's Mod v5.3, that was hacked by Ferus."
	saves_version = "1.1.0"

	# Main command list
	commandlist = "Pyborg commands:\n!checkdict, !contexts, !help, !known, !learning, !rebuilddict, !replace, !unlearn, !purge,\
 !version, !words, !limit, !save, !owner"
	commanddict = {
		"help": "Owner command. Usage: !help [command]\nPrints information about using a command, or a list of commands if no command is given",
		"version": "Usage: !version\nDisplay what version of Pyborg we are running",
		"words": "Usage: !words\nDisplay how many words are known",
		"known": "Usage: !known word1 [word2 [...]]\nDisplays if one or more words are known, and how many contexts are known",
		"contexts": "Owner command. Usage: !contexts <phrase>\nPrint contexts containing <phrase>",
		"unlearn": "Owner command. Usage: !unlearn <expression>\nRemove all occurances of a word or expression from the dictionary. For example '!unlearn of of' would remove all contexts containing double 'of's",
		"purge": "Owner command. Usage: !purge [number]\nRemove all occurances of the words that appears in less than <number> contexts",
		"replace": "Owner command. Usage: !replace <old> <new>\nReplace all occurances of word <old> in the dictionary with <new>",
		"learning": "Owner command. Usage: !learning [on|off]\nToggle bot learning. Without arguments shows the current setting",
		"checkdict": "Owner command. Usage: !checkdict\nChecks the dictionary for broken links. Shouldn't happen, but worth trying if you get KeyError crashes",
		"rebuilddict": "Owner command. Usage: !rebuilddict\nRebuilds dictionary links from the lines of known text. Takes a while. You probably don't need to do it unless your dictionary is very screwed",
		"limit": "Owner command. Usage: !limit [number]\nSet the number of words that pyBorg can learn",
		"owner": "Usage : !owner password\nAdd the user in the owner list"
	}

	def __init__(self, settings):
		"""
		Open the dictionary. Resize as required.
		"""
		self.settings = settings
		self.unfilterd = {}

		# Read the dictionary
		print(">>> [Gentbot] Reading dictionary...")
		try:
			with open(self.settings['data_dir'] + "words.dat", "rb") as f:
				self.words = marshal.loads(f.read())
			with open(self.settings['data_dir'] + "lines.dat", "rb") as f:
				self.lines = marshal.loads(f.read())
		except (ValueError, EOFError, IOError) as e:
			# Create mew database
			self.words = {}
			self.lines = {}
			print("Error reading saves. New database created.")
			print(repr(e))

		# Is a resizing required?
		if len(self.words) != self.settings['num_words']:
			print("Updating dictionary information...")
			self.settings['num_words'] = len(self.words)
			num_contexts = 0
			# Get number of contexts
			for x in list(self.lines.keys()):
				num_contexts += len(self.lines[x][0].split())
			self.settings['num_contexts'] = num_contexts
			# Save new values

	def save_all(self):
		if self.settings['no_save'] != True:
			print(">>> [Gentbot] Writing dictionary...")
			with open(self.settings['data_dir'] + "words.dat", "wb") as f:
				f.write(marshal.dumps(self.words))
			with open(self.settings['data_dir'] + "lines.dat", "wb") as f:
				f.write(marshal.dumps(self.lines))

	def process_msg(self, io_module, body, replyrate, learn, args, owner=0):
		"""
		Process message 'body' and pass back to IO module with args.
		If owner==1 allow owner commands.
		"""
		# add trailing space so sentences are broken up correctly
		body += " "

		# Parse commands
		if body[0] == "!":
			self.do_commands(io_module, body, args, owner)
			return

		# Filter out garbage and do some formatting
		body = filter_message(body, self)
	
		# Learn from input
		if learn == 1:
			self.learn(body)

		# Make a reply if desired
		if randint(0, 99) < replyrate:
			message = self.reply(body)

			# single word reply: always output
			if len(message.split()) == 1:
				io_module.output(message, args)
				return
			# empty. do not output
			if message == "":
				return
			# else output
			io_module.output(message, args)

	def do_commands(self, io_module, body, args, owner):
		"""
		Respond to user comands.
		"""
		msg = ""

		command_list = body.split()
		command_list[0] = command_list[0].lower()
		args += ("\x19\x08\x15\x21\x10\x15\x20\x01\x03\x08\x09",) # Tell io_module that this is not markov output

		# Version string
		if command_list[0] == "!version":
			msg = self.ver_string

		# How many words do we know?
		elif command_list[0] == "!words":
			num_w = self.settings['num_words']
			num_c = self.settings['num_contexts']
			num_l = len(self.lines)
			if num_w != 0:
				num_cpw = num_c/float(num_w) # contexts per word
			else:
				num_cpw = 0.0
			msg = "I know %d words (%d contexts, %.2f per word), %d lines." % (num_w, num_c, num_cpw, num_l)
				
		# Do i know this word
		elif command_list[0] == "!known":
			if len(command_list) == 2:
				# single word specified
				word = command_list[1].lower()
				if word in self.words:
					c = len(self.words[word])
					msg = "%s is known (%d contexts)" % (word, c)
				else:
					msg = "%s is unknown." % word
			elif len(command_list) > 2:
				# multiple words.
				words = []
				for x in command_list[1:]:
					words.append(x.lower())
				msg = "Number of contexts: "
				for x in words:
					if x in self.words:
						c = len(self.words[x])
						msg += x+"/"+str(c)+" "
					else:
						msg += x+"/0 "
	
		# Owner commands
		if owner == 1:
			# Save dictionary
			if command_list[0] == "!save":
				self.save_all()
				msg = "Dictionary saved"

			# Command list
			elif command_list[0] == "!help":
				if len(command_list) > 1:
					# Help for a specific command
					cmd = command_list[1].lower()
					dic = None
					if cmd in list(self.commanddict.keys()):
						dic = self.commanddict
					elif cmd in list(io_module.commanddict.keys()):
						dic = io_module.commanddict
					if dic:
						for i in dic[cmd].split("\n"):
							io_module.output(i, args)
					else:
						msg = "No help on command '%s'" % cmd
				else:
					for i in self.commandlist.split("\n"):
						io_module.output(i, args)
					for i in io_module.commandlist.split("\n"):
						io_module.output(i, args)

			# Change the max_words setting
			elif command_list[0] == "!limit":
				msg = "The max limit is "
				if len(command_list) == 1:
					msg += str(self.settings['max_words'])
				else:
					limit = int(command_list[1].lower())
					self.settings['max_words'] = limit
					msg += "now " + command_list[1]

			
			# Check for broken links in the dictionary
			elif command_list[0] == "!checkdict":
				t = time.time()
				num_broken = 0
				num_bad = 0
				for w in list(self.words.keys()):
					wlist = self.words[w]

					for i in range(len(wlist)-1, -1, -1):
						line_idx, word_num = struct.unpack("lH", wlist[i])

						# Nasty critical error we should fix
						if line_idx not in self.lines:
							print("Removing broken link '%s' -> %d" % (w, line_idx))
							num_broken = num_broken + 1
							del wlist[i]
						else:
							# Check pointed to word is correct
							split_line = self.lines[line_idx][0].split()
							if split_line[word_num] != w:
								print("Line '%s' word %d is not '%s' as expected." % \
									(self.lines[line_idx][0],
									word_num, w))
								num_bad = num_bad + 1
								del wlist[i]
					if len(wlist) == 0:
						del self.words[w]
						print("\"%s\" vaped totally" % w)

				msg = "Checked dictionary in %0.2fs. Fixed links: %d broken, %d bad." % \
					(time.time()-t,
					num_broken,
					num_bad)

			# Rebuild the dictionary by discarding the word links and
			# re-parsing each line
			elif command_list[0] == "!rebuilddict":
				if self.settings['learning'] == 1:
					t = time.time()

					old_lines = self.lines
					old_num_words = self.settings['num_words']
					old_num_contexts = self.settings['num_contexts']

					self.words = {}
					self.lines = {}
					self.settings['num_words'] = 0
					self.settings['num_contexts'] = 0

					for k in list(old_lines.keys()):
						self.learn(old_lines[k][0], old_lines[k][1])

					msg = "Rebuilt dictionary in %0.2fs. Words %d (%+d), contexts %d (%+d)" % \
							(time.time()-t,
							old_num_words,
							self.settings['num_words'] - old_num_words,
							old_num_contexts,
							self.settings['num_contexts'] - old_num_contexts)

			#Remove rares words
			elif command_list[0] == "!purge":
				t = time.time()

				liste = []
				compteur = 0

				if len(command_list) == 2:
				# limite d occurences a effacer
					c_max = command_list[1].lower()
				else:
					c_max = 0

				c_max = int(c_max)

				for w in list(self.words.keys()):
				
					digit = 0
					char = 0
					for c in w:
						if c.isalpha():
							char += 1
						if c.isdigit():
							digit += 1

				
				#Compte les mots inferieurs a cette limite
					c = len(self.words[w])
					if c < 2 or ( digit and char ):
						liste.append(w)
						compteur += 1
						if compteur == c_max:
							break

				if c_max < 1:
					#io_module.output(str(compteur)+" words to remove", args)
					io_module.output("%s words to remove" %compteur, args)
					return

				#supprime les mots
				for w in liste[0:]:
					self.unlearn(w)

				msg = "Purged dictionary in %0.2fs. %d words removed" % \
						(time.time()-t,
						compteur)
				
			# Change a typo in the dictionary
			elif command_list[0] == "!replace":
				if len(command_list) < 3:
					return
				old = command_list[1].lower()
				new = command_list[2].lower()
				msg = self.replace(old, new)

			# Print contexts [flooding...:-]
			elif command_list[0] == "!contexts":
				# This is a large lump of data and should
				# probably be printed, not module.output XXX

				# build context we are looking for
				context = " ".join(command_list[1:])
				context = context.lower()
				if context == "":
					return
				io_module.output("Contexts containing \""+context+"\":", args)
				# Build context list
				# Pad it
				context = " "+context+" "
				c = []
				# Search through contexts
				for x in list(self.lines.keys()):
					# get context
					ctxt = self.lines[x][0]
					# add leading whitespace for easy sloppy search code
					ctxt = " "+ctxt+" "
					if ctxt.find(context) != -1:
						# Avoid duplicates (2 of a word
						# in a single context)
						if len(c) == 0:
							c.append(self.lines[x][0])
						elif c[len(c)-1] != self.lines[x][0]:
							c.append(self.lines[x][0])
				x = 0
				while x < 5:
					if x < len(c):
						io_module.output(c[x], args)
					x += 1
				if len(c) == 5:
					return
				if len(c) > 10:
					io_module.output("...("+repr(len(c)-10)+" skipped)...", args)
				x = len(c) - 5
				if x < 5:
					x = 5
				while x < len(c):
					io_module.output(c[x], args)
					x += 1

			# Remove a word from the vocabulary [use with care]
			elif command_list[0] == "!unlearn":
				# build context we are looking for
				context = " ".join(command_list[1:])
				context = context.lower()
				if context == "":
					return
				print("Looking for: "+context)
				# Unlearn contexts containing 'context'
				t = time.time()
				self.unlearn(context)
				# we don't actually check if anything was
				# done..
				msg = "Unlearn done in %0.2fs" % (time.time()-t)

			# Query/toggle bot learning
			elif command_list[0] == "!learning":
				msg = "Learning mode "
				if len(command_list) == 1:
					if self.settings['learning'] == 0:
						msg += "off"
					else:
						msg += "on"
				else:
					toggle = command_list[1].lower()
					if toggle == "on":
						msg += "on"
						self.settings['learning'] = 1
					else:
						msg += "off"
						self.settings['learning'] = 0

			# Quit
			elif command_list[0] == "!quit":
				# Close the dictionary
				self.save_all()
				sys.exit()
				
		if msg != "":	
			io_module.output(msg, args)


	def replace(self, old, new):
		"""
		Replace all occuraces of 'old' in the dictionary with
		'new'. Nice for fixing learnt typos.
		"""
		try:
			pointers = self.words[old]
		except KeyError as e:
			return old+" not known."
		changed = 0

		for x in pointers:
			# pointers consist of (line, word) to self.lines
			l, w = struct.unpack("lH", x)
			line = self.lines[l][0].split()
			number = self.lines[l][1]
			if line[w] != old:
				# fucked dictionary
				print("Broken link: %s %s" % (x, self.lines[l][0] ))
				continue
			else:
				line[w] = new
				self.lines[l][0] = " ".join(line)
				self.lines[l][1] += number
				changed += 1

		if new in self.words:
			self.settings['num_words'] -= 1
			self.words[new].extend(self.words[old])
		else:
			self.words[new] = self.words[old]
		del self.words[old]
		return "%d instances of %s replaced with %s" % ( changed, old, new )

	def unlearn(self, context):
		"""
		Unlearn all contexts containing 'context'. If 'context'
		is a single word then all contexts containing that word
		will be removed, just like the old !unlearn <word>
		"""
		# Pad thing to look for
		# We pad so we don't match 'shit' when searching for 'hit', etc.
		context = " "+context+" "
		# Search through contexts
		# count deleted items
		dellist = []
		# words that will have broken context due to this
		wordlist = []
		for x in list(self.lines.keys()):
			# get context. pad
			c = " "+self.lines[x][0]+" "
			if c.find(context) != -1:
				# Split line up
				wlist = self.lines[x][0].split()
				# add touched words to list
				for w in wlist:
					if not w in wordlist:
						wordlist.append(w)
				dellist.append(x)
				del self.lines[x]
		words = self.words
		unpack = struct.unpack
		# update links
		for x in wordlist:
			word_contexts = words[x]
			# Check all the word's links (backwards so we can delete)
			for y in range(len(word_contexts)-1, -1, -1):
				# Check for any of the deleted contexts
				if unpack("lH", word_contexts[y])[0] in dellist:
					del word_contexts[y]
					self.settings['num_contexts'] = self.settings['num_contexts'] - 1
			if len(words[x]) == 0:
				del words[x]
				self.settings['num_words'] = self.settings['num_words'] - 1
				print("\"%s\" vaped totally" %x)

	def reply(self, body):
		"""
		Reply to a line of text.
		"""
		# split sentences into list of words
		_words = body.split(" ")
		words = []
		for i in _words:
			words += i.split()
		del _words

		if len(words) == 0:
			return ""
		
		#remove words on the ignore list
		words = [x for x in words if x not in self.settings['ignore_list'] and not x.isdigit()]

		# Find rarest word (excluding those unknown)
		index = []
		known = -1
		#The word has to bee seen in already 3 contexts differents for being choosen
		known_min = 3
		for x in range(0, len(words)):
			if words[x] in self.words:
				k = len(self.words[words[x]])
			else:
				continue
			if (known == -1 or k < known) and k > known_min:
				index = [words[x]]
				known = k
				continue
			elif k == known:
				index.append(words[x])
				continue
		# Index now contains list of rarest known words in sentence
		if len(index)==0:
			return ""
		word = index[randint(0, len(index)-1)]

		# Build sentence backwards from "chosen" word
		sentence = [word]
		done = 0
		while done == 0:
			#create a dictionary wich will contain all the words we can found before the "chosen" word
			pre_words = {"" : 0}
			#this is for prevent the case when we have an ignore_listed word
			word = str(sentence[0].split(" ")[0])
			for x in range(0, len(self.words[word]) -1 ):
				l, w = struct.unpack("lH", self.words[word][x])
				context = self.lines[l][0]
				num_context = self.lines[l][1]
				cwords = context.split()
				#if the word is not the first of the context, look the previous one
				if cwords[w] != word:
					print(context)
				if w:
					#look if we can found a pair with the choosen word, and the previous one
					if len(sentence) > 1 and len(cwords) > w+1:
						if sentence[1] != cwords[w+1]:
							continue

					#if the word is in ignore_list, look the previous word
					look_for = cwords[w-1]
					if look_for in self.settings['ignore_list'] and w > 1:
						look_for = cwords[w-2]+" "+look_for

					#saves how many times we can found each word
					if not(look_for in pre_words):
						pre_words[look_for] = num_context
					else :
						pre_words[look_for] += num_context


				else:
					pre_words[""] += num_context

			#Sort the words
			liste = list(pre_words.items())
			liste.sort(key = lambda x,y: cmp(y[1],x[1]))
			
			numbers = [liste[0][1]]
			for x in range(1, len(liste) ):
				numbers.append(liste[x][1] + numbers[x-1])

			#take one them from the list ( randomly )
			mot = randint(0, numbers[len(numbers) -1])
			for x in range(0, len(numbers)):
				if mot <= numbers[x]:
					mot = liste[x][0]
					break

			#if the word is already choosen, pick the next one
			while mot in sentence:
				x += 1
				if x >= len(liste) -1:
					mot = ''
				mot = liste[x][0]

			mot = mot.split(" ")
			mot.reverse()
			if mot == ['']:
				done = 1
			else:
				list(map( (lambda x: sentence.insert(0, x) ), mot ))

		pre_words = sentence
		sentence = sentence[-2:]

		# Now build sentence forwards from "chosen" word

		#We've got
		#cwords:	...	cwords[w-1]	cwords[w]	cwords[w+1]	cwords[w+2]
		#sentence:	...	sentence[-2]	sentence[-1]	look_for	look_for ?

		#we are looking, for a cwords[w] known, and maybe a cwords[w-1] known, what will be the cwords[w+1] to choose.
		#cwords[w+2] is need when cwords[w+1] is in ignored list


		done = 0
		while done == 0:
			#create a dictionary wich will contain all the words we can found before the "chosen" word
			post_words = {"" : 0}
			word = str(sentence[-1].split(" ")[-1])
			for x in range(0, len(self.words[word]) ):
				l, w = struct.unpack("lH", self.words[word][x])
				context = self.lines[l][0]
				num_context = self.lines[l][1]
				cwords = context.split()
				#look if we can found a pair with the choosen word, and the next one
				if len(sentence) > 1:
					if sentence[len(sentence)-2] != cwords[w-1]:
						continue

				if w < len(cwords)-1:
					#if the word is in ignore_list, look the next word
					look_for = cwords[w+1]
					if look_for in self.settings['ignore_list'] and w < len(cwords) -2:
						look_for = look_for+" "+cwords[w+2]

					if not(look_for in post_words):
						post_words[look_for] = num_context
					else :
						post_words[look_for] += num_context
				else:
					post_words[""] += num_context
			#Sort the words
			liste = list(post_words.items())
			liste.sort(lambda x,y: cmp(y[1],x[1]))
			numbers = [liste[0][1]]
			
			for x in range(1, len(liste) ):
				numbers.append(liste[x][1] + numbers[x-1])

			#take one them from the list ( randomly )
			mot = randint(0, numbers[len(numbers) -1])
			for x in range(0, len(numbers)):
				if mot <= numbers[x]:
					mot = liste[x][0]
					break

			x = -1
			while mot in sentence:
				x += 1
				if x >= len(liste) -1:
					mot = ''
					break
				mot = liste[x][0]


			mot = mot.split(" ")
			if mot == ['']:
				done = 1
			else:
				list(map( (lambda x: sentence.append(x) ), mot ))

		sentence = pre_words[:-2] + sentence

		#Insert space between each words
		list(map( (lambda x: sentence.insert(1+x*2, " ") ), list(range(0, len(sentence)-1)) )) 

		#correct the ' & , spaces problem
		#code is not very good and can be improve but does his job...
		for x in range(0, len(sentence)):
			if sentence[x] == "'":
				sentence[x-1] = ""
				if x + 1 <= len(sentence):
					sentence[x+1] = ""
			if sentence[x] == ",":
				sentence[x-1] = ""

		#return as string..
		return "".join(sentence)

	def learn(self, body, num_context=1):
		"""
		Lines should be cleaned (filter_message()) before passing
		to this.
		"""

		def learn_line(self, body, num_context):
			"""
			Learn from a sentence.
			"""
			words = body.split()
			# Ignore sentences of < 1 words XXX was <3
			#testing 2
			if len(words) < 2:
				return

			voyelles = "aÃ Ã¢eÃ©Ã¨ÃªiÃ®Ã¯oÃ¶Ã´uÃ¼Ã»y"
			for x in range(0, len(words)):

				nb_voy = 0
				digit = 0
				char = 0
				for c in words[x]:
					if c in voyelles:
						nb_voy += 1
					if c.isalpha():
						char += 1
					if c.isdigit():
						digit += 1

				if len(words[x]) > 13 \
				or ( ((nb_voy*100) / len(words[x]) < 26) and len(words[x]) > 5 ) \
				or ( char and digit ) \
				or ( (words[x] in self.words) == 0 and self.settings['learning'] == 0 ):
					#if one word as more than 13 characters, don't learn
					#		( in french, this represent 12% of the words )
					#and d'ont learn words where there are less than 25% of voyels
					#don't learn the sentence if one word is censored
					#don't learn too if there are digits and char in the word
					#same if learning is off
					return
				elif ( "-" in words[x] or "_" in words[x] ) :
					words[x]="#nick"


			num_w = self.settings['num_words']
			if num_w != 0:
				num_cpw = self.settings['num_contexts']/float(num_w) # contexts per word
			else:
				num_cpw = 0

			cleanbody = " ".join(words)

			# Hash collisions we don't care about. 2^32 is big :-)
			hashval = hash(cleanbody)

			# Check context isn't already known
			if hashval not in self.lines:
				if not(num_cpw > 100 and self.settings['learning'] == 0):
					
					self.lines[hashval] = [cleanbody, num_context]
					# Add link for each word
					for x in range(0, len(words)):
						if words[x] in self.words:
							# Add entry. (line number, word number)
							self.words[words[x]].append(struct.pack("lH", hashval, x))
						else:
							self.words[words[x]] = [ struct.pack("lH", hashval, x) ]
							self.settings['num_words'] += 1
						self.settings['num_contexts'] += 1
			else :
				self.lines[hashval][1] += num_context

			#is max_words reached, don't learn more
			if self.settings['num_words'] >= self.settings['max_words']: self.settings['learning'] = 0

		# Split body text into sentences and parse them
		# one by one.
		body += " "
		list(map ( (lambda x : learn_line(self, x, num_context)), body.split(". ")))

