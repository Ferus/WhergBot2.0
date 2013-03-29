Settings = {
	"url_regex": "(https?|ftp):\/\/(([\w\-]+\.)+[a-zA-Z]{2,6}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?(\/([\w\-~.#\/?=&;:+%!*\[\]@$\'()+,|\^]+)?)?"
	,"no_title": "No Title"
	,"show_no_title": False
	,"blacklist": ["youtube.com"
		,"youtu.be"
		,"imgur.com"
		,"4chon.net"
		,"wikipedia.org"
		,"\.(?:mp4|wmv|flv|mp3|wav|flac)"
		]
	# blacklist is a list of regex's to re.search() for, it should "just work" by
	# adding the base domain of the site you want to block
	}
