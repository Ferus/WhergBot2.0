Settings = {
	'allowed':['Ferus!anonymous@the.interwebs']
	,'gentbot': {
		'replyrate': 15
		,"data_dir": "Plugins/Gentbot/data/" #data dir
		,"num_contexts": 0 # Total word contextx
		,"num_words": 0 # Total unique words known
		,"max_words": 12000 # Max limit in the number of words known
		,"learning": True # Allow the bot to learn?
		,"ignore_list": ['!.', '?.', "'", ',', ';', 'asl', 'h'] # Words to ignore
		,"no_save": False # If true, dont save to disk
	}
	,'twitter': {
		'use': True,
		'oauth-keys': {
			"consumer_key": 'h',
			"consumer_secret": 'h',
			"access_token_key": 'h',
			"access_token_secret": 'h'
		}
	}
}
