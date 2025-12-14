# Hava Parker - COM528 Final Project

import argparse, statistics
from scraper import *
from bs4 import BeautifulSoup

class Poster: # done ... ?
	def __init__(self, username, align, postcount, wordcount):
		self.username = username
		self.align = align
		self.postcount = postcount
		self.wordcount = wordcount
		self.interactions = {}
		self.interactions['w'] = 0
		self.interactions['v'] = 0

	def __str__(self):
		return f'{self.username} ({self.align}): {self.postcount} post(s), {self.wordcount} word(s)\n {self.interactions}'

	def updateCounts(self, wordcount):
		self.postcount += 1
		self.wordcount += wordcount

	def getAvgWordsPerPost(self):
		avgWordsPerPost = 0
		if self.postcount:
			avgWordsPerPost = self.wordcount / self.postcount
		return avgWordsPerPost

	def getPercentWolfInteractions(self):
		percentage = -1
		wolfInteractions = self.interactions['w']
		villaInteractions = self.interactions['v']
		totalInteractions = wolfInteractions + villaInteractions
		if totalInteractions:
			percentage = 100 * (wolfInteractions / totalInteractions)
		return percentage

def alignmentFromHex(hexCode):
	rgbTuple = tuple(int(hexCode[i:i+2], 16) for i in (0, 2, 4))
	r, g, b = rgbTuple
	return "w" if r > g else "v"

class ThreadAnalyzer:
	def __init__(self, posts):
		self.posts = posts
		self.roster = []
		self.alignments = {}

	def trimThread(self):
		gameOverPostId = 0
		for post in self.posts:
			if 'Game Over' in str(post[3]) and post[1] == 'Mafia Host':
				gameOverPostId = self.posts[post[0] - 1][0]
		try:
			nextId = self.posts[gameOverPostId + 1][0]
			isDuplicated = (gameOverPostId == nextId)
			while isDuplicated:
				gameOverPostId += 1
				nextId = self.posts[gameOverPostId + 1][0]
				isDuplicated = (gameOverPostId == nextId)
		except IndexError:
			print("already at end of thread!")
		finally:
			self.posts = self.posts[:gameOverPostId + 1]


	def getRoster(self, gameOverPost):
		gameOverSoup = BeautifulSoup(gameOverPost, 'html.parser')
		blocks = gameOverSoup.find_all('div', class_ = 'profile-block')
		for block in blocks:
			if "Rands" in block.text:
				rands = block
		roleCards = rands.find_all('div', class_ = 'bbc_spoiler')
		for card in roleCards:
			card.extract()
		playerlist = rands.find_all('span', {'style': True})
		for player in playerlist:
			username = player.text
			hexCode = player['style'].split()[1][1:-1]
			align = alignmentFromHex(hexCode)
			poster = Poster(username, align, 0, 0)
			self.alignments[username] = align
			self.roster.append(poster)

	def traversePosts(self):
		for post in self.posts:
			username = post[1]
			quotedUsername = post[2]
			for poster in self.roster:
				if username == poster.username:
					wordcount = len(post[3].split())
					poster.updateCounts(wordcount)
					if quotedUsername in self.alignments:
						align = self.alignments[quotedUsername]
						poster.interactions[align] += 1

	def findVotes(self):
		pass

	def getSentiment(self):
		pass

def getBaselineInteractionPercent(alignments):
	wolfCount = 0
	villaCount = 0
	for username in alignments:
		if alignments[username] == 'w':
			wolfCount += 1
		else: villaCount += 1
	totalCount = wolfCount + villaCount
	return round(100 * (wolfCount / totalCount), 2)

def summarizeThread(analyzer):
	wolfPosters = []
	villaPosters = []
	totalPostcount = 0
	for poster in analyzer.roster:
		totalPostcount += poster.postcount
		if poster.align == 'w':
			wolfPosters.append(poster)
		else:
			villaPosters.append(poster)
	
	baseline = getBaselineInteractionPercent(analyzer.alignments)

	wolfPostcountPercents = []
	wolfWordsPerPosts = []
	wolfWolfInteractionPercent = []
	
	villaPostcountPercents = []
	villaWordsPerPosts = []
	villaWolfInteractionPercent = []

	for wolf in wolfPosters:
		wolfPostcountPercents.append(100 * (wolf.postcount / totalPostcount))
		if wolf.postcount:
			wolfWordsPerPosts.append(wolf.wordcount / wolf.postcount)
		else:
			wolfWordsPerPosts.append(0)
		wolfInteractionPercent = wolf.getPercentWolfInteractions()
		wolfWolfInteractionPercent.append(100 * (wolfInteractionPercent / baseline))

	for villa in villaPosters:
		villaPostcountPercents.append(100 * (villa.postcount / totalPostcount))
		if villa.postcount:
			villaWordsPerPosts.append(villa.wordcount / villa.postcount)
		else:
			villaWordsPerPosts.append(0)
		wolfInteractionPercent = villa.getPercentWolfInteractions()
		villaWolfInteractionPercent.append(100 * (wolfInteractionPercent / baseline))

	averages = {}
	averages['w'] = {}
	averages['v'] = {}

	averages['w']['postcountPercent'] = round(statistics.mean(wolfPostcountPercents), 2)
	averages['w']['wordsPerPost'] = round(statistics.mean(wolfWordsPerPosts), 2)
	averages['w']['wolfInteractionPercent'] = round(statistics.mean(wolfWolfInteractionPercent), 2)

	averages['v']['postcountPercent'] = round(statistics.mean(villaPostcountPercents), 2)
	averages['v']['wordsPerPost'] = round(statistics.mean(villaWordsPerPosts), 2)
	averages['v']['wolfInteractionPercent'] = round(statistics.mean(villaWolfInteractionPercent), 2)

	return(averages)