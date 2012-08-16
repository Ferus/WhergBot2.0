#!/usr/bin/env python
# -*- coding: utf8 -*-

# A very incomplete API for thefuckingweather.com
# dealw/it.

import requests, re

def getWeather(zipcode):
	r = requests.get("http://testing.thefuckingweather.com/?where={0}".format(zipcode))
	try:
		r.raise_for_status()
	except (requests.HTTPError, requests.ConnectionError) as e:
		return "Error: {0}".format(e.args[0])
	temp = re.search("<span class=\"temperature\" tempf=\"\d{1,3}\">(\d{1,3})</span>", r.text).groups()[0]
	remark = re.search("<p class=\"remark\">(.*?)</p>", r.text).groups()[0]
	location = re.search("<span id=\"locationDisplaySpan\" class=\"small\">(.*?)</span>", r.text).groups()[0]
	return "{0}°?! {1} in {2}".format(temp, remark, location)

