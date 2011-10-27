#!/usr/bin/python2
#Tinyboard thread stats checker. 

import re
import requests

class Tinyboard(object):
	def GetHtml(self, link):
		if not link:
			return None
		else:
			try:
				html = requests.get(link)
				html = html.content
				return html
			except:
				return None
				
	def Parse(self, link):
		link = link.replace("mod.php?/", "")	
		html = self.GetHtml(link)
		
		imageCount = html.count("<p class=\"fileinfo\">") #Number of images
		postCount = html.count("<div class=\"post reply\"") #Number of post replies
		if imageCount > 1:
			imageText = "{0} images".format(imageCount)
		elif imageCount == 0:
			imageText = "no images"
		else:
			imageText = "1 image"
			
		if postCount > 1:
			postText = "{0} replies".format(postCount)
		elif postCount == 0:
			postText = "no replies"
		else:
			postText = "1 reply"
		
		OP_html = html.split("<div class=\"post op\">")[1].split("</div>")[0]
		try:
			OP_Name = OP_html.split("<span class=\"name\">")[1].split("</span>")[0].strip(" ")
		except:
			OP_Name = "Anonymous"
			
		try:
			OP_Trip = OP_html.split("<span class=\"trip\">")[1].split("</span>")[0].strip(" ")
		except:
			OP_Trip = None
			
		try:
			OP_CapCode = OP_html.split("<a class=\"capcode\">")[1].split("</a>")[0].strip(" ")
		except:
			OP_CapCode = None
			
		try:
			OP_Post = OP_html.split("<p class=\"body\">")[1].split("</p>")[0]
			OP_Post = OP_Post.replace("<br/>"," ").replace("&#8220;", "\"").replace("\'","'")
			OP_Post = OP_Post.replace("<span class=\"spoiler\">", "").replace("<span class=\"heading\">", "").replace("</span>","")
			OP_Post = OP_Post.replace("<strong>","").replace("</strong>","").replace("<em>","").replace("</em>","")
			OP_Post = self.smart_truncate(OP_Post)
		except:
			OP_Post = "Couldn't parse OP's post."
			
		if OP_Trip:
			return "{0} {1} ({2}, {3}) posted: {4} - {5}".format(OP_Name, OP_Trip, postText, imageText, OP_Post, link)
		elif OP_CapCode:
			return "{0} {1} ({2}, {3}) posted: {4} - {5}".format(OP_Name, OP_CapCode, postText, imageText, OP_Post, link)
		else:
			return "{0} ({1}, {2}) posted: {3} - {4}".format(OP_Name, postText, imageText, OP_Post, link)
	
	def smart_truncate(self, content, length=300, suffix='...'):
		'''Borrowed from stackoverflow, Credits to 'Adam'. :) '''
		if len(content) <= length:
			return content
		else:
			return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix
	
	def Main(self, link=None):
		try:
			return self.Parse(link)
		except:
			return None
			
			
