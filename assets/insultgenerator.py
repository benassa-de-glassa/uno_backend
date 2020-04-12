#!/usr/bin/env python3


import requests
from random import random

def insultgenerator(sender, receiver):

	# Name of the player sending an insult
	sname = sender['name']
	# Name of the insult's victim
	rname = receiver['name']

	# Get a random number to randomize behaviour of insult button
	rnd = random()

	# If the insulting player is done, this message might be displayed
	if sender['finished'] and rnd < 0.7:
		insulttext = 'Why don\'t you shut up, %s, you have no reason to complain!' % (sname)
	# There is a 20% chance that no random words are included in the message
	elif rnd < 0.2:
		if rnd < 0.1:
			insulttext = '%s blames %s for their poor performance.' % (sname, rname)
		else:
			insulttext = '%s is fuming about this!' % (sname)
	else:
		# Get adjectives and nouns from APIs, use one adjetive to search for a related noun
		adjectives_api = 'https://insult.mattbas.org/api/adjective'
		adj1 = requests.get(adjectives_api).text
		adj2 = requests.get(adjectives_api).text
		adj3 = requests.get(adjectives_api).text

		noun_api = 'http://api.datamuse.com/words?max=1&rel_jja=' + adj3 
		noun = requests.get(noun_api).json()[0]['word']
		
		# Further special cases for not having cards yet, having received a penalty for late UNO, or being the king
		if not sender['has_received_initial_cards'] and rnd < 0.6:
			insulttext = 'Even before his game has started, %s feels the need to call %s a %s, %s, %s...' % (sname, rname, adj2, adj3, noun)
		elif sender['penalty'] > 0:
			insulttext = 'Being a %s %s, %s is unable to say "UNO" fast enough...' % (adj3, noun, sname)
		elif sender['king']:
			insulttext = 'By royal decree, the crown declares %s a %s, %s %s!' % (rname, adj1, adj2, noun)
		else:
			# Standard insult
			insulttext = '%s just called %s a %s, %s %s!' % (sname, rname, adj1, adj2, noun)
	return insulttext