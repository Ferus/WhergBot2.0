#!/usr/bin/python2
#Tinyboard thread stats checker. 

import re
import requests

class Tinyboard(object):
	'''
	A simple module that returns stats of a thread.	Post count, Image count, and the OP's text.
	If the link contains a hash (#) at the end (A direct link to a specific post), 
	it will return that posts text rather than the OP.
	'''

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
		
		if re.search("#", link):
			link = link.replace("#q","#")
			threadnum, postnum = link.split("/")[-1].split(".html#")
			if not threadnum == postnum:
				Post_html = html.split("<div class=\"post reply\" id=\"reply_{0}\">".format(postnum))[1].split("</div>")[0]
			else:
				Post_html = html.split("<div class=\"post op\">")[1].split("</div>")[0]
		else:
			Post_html = html.split("<div class=\"post op\">")[1].split("</div>")[0]
			
		try:
			Post_Name = Post_html.split("<span class=\"name\">")[1].split("</span>")[0].strip(" ")
		except:
			Post_Name = "Anonymous"
			
		try:
			Post_Trip = Post_html.split("<span class=\"trip\">")[1].split("</span>")[0].strip(" ")
		except:
			Post_Trip = None
			
		try:
			Post_CapCode = Post_html.split("<a class=\"capcode\">")[1].split("</a>")[0].strip(" ")
		except:
			Post_CapCode = None
			
		try:
			Post_Text = Post_html.split("<p class=\"body\">")[1].split("</p>")[0]
			Post_Text = Post_Text.replace("<br/>"," ").replace("&#8220;", "\"").replace("&quot;","\"").replace("\'","'")
			Post_Text = Post_Text.replace("<span class=\"spoiler\">", "").replace("<span class=\"heading\">", "")
			Post_Text = Post_Text.replace("<span class=\"quote\">&gt;",">").replace("&amp;","&").replace("</span>","")
			Post_Text = Post_Text.replace("<strong>","").replace("</strong>","").replace("<em>","").replace("</em>","")
			#>>> cont = re.compile("<a .*?&gt;&gt;(.*?)<.*>")
			#>>> result = cont.search(x)
			#>>> result.groups()[0]
			#'169'	
			if re.search("<a onclick=.* href=.*>&gt;&gt;.*</a>", Post_Text): 
				Link_Num = ">>"+re.findall("&gt;[0-9]{1,}<", Post_Text)[0][:-1][4:]
				Post_Text = re.sub("<a onclick=\"highlightReply.*;\" href=.*>&gt;&gt;.*</a>", Link_Num, Post_Text)
			
			Post_Text = self.smart_truncate(Post_Text)
		except:
			Post_Text = "Couldn't parse OP's post."
			
		if Post_Trip:
			return "{0} {1} ({2}, {3}) posted: {4} - {5}".format(Post_Name, Post_Trip, postText, imageText, Post_Text, link)
		elif Post_CapCode:
			return "{0} {1} ({2}, {3}) posted: {4} - {5}".format(Post_Name, Post_CapCode, postText, imageText, Post_Text, link)
		else:
			return "{0} ({1}, {2}) posted: {3} - {4}".format(Post_Name, postText, imageText, Post_Text, link)
	
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
			
			
