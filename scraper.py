# Hava Parker - COM528 Final Project

import argparse, cloudscraper, random, requests, time
from bs4 import BeautifulSoup
 
# randomize user agent string
headerOptions = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36"\
                ]

class PageScraper:
	def __init__(self, url):
		self.url = url
		self.baseUrl = "https://mafiauniverse.com/forums/"

		headers = requests.utils.default_headers()
		uagent = random.choice(headerOptions)

		headers.update({
			'User-Agent': uagent
			})

		req = requests.Session()
		page = req.get(url, headers = headers)

		self.soup = BeautifulSoup(page.content, 'html.parser')
		self.postlist = self.soup.find(id = 'posts')
		self.posts = self.postlist.find_all(attrs = {'data-postnumber': True})

	# test this again later
	def cleanText(text):
		cleanedText = ' '.join(text.split())
		return cleanedText

	def getNextUrl(self):
		""" find the url of the following page.
		returns relative url if there exists a next page.
		returns None otherwise. """

		paginator = self.soup.find('div', id = 'pagination_top')
		prevNexts = paginator.find_all('span', class_ = 'prev_next')
		nextUrl = None
		for prevNext in prevNexts:
			if prevNext.find('a', {'rel': 'next'}):
				nextUrl = self.baseUrl + prevNext.find('a', {'rel': 'next'})['href']
		return nextUrl

	def scrape(self):
		""" gets list of all posts on a single forum page.
		post representation is formatted as
		[postnum, poster username, username of quoted poster, cleaned content]
		returns list of posts on page. """

		pagePostsArr = []

		for post in self.posts:
			# can't recall validity
			checkPostValid = post.find('a', class_ = 'postcounter')
			if checkPostValid:
				postnum = post.find('a', class_ = 'postcounter').text
			else:
				continue

			username = post.find('a', class_ = 'username').text
			# this is None if the current post does not contain an inner quote
			quoteExists = post.find('div', class_ = 'bbcode_postedby')

			if quoteExists:
				quotedUsername = post.find('div', class_ = 'bbcode_postedby').find('strong').text
				innerquote = post.find('div', class_ = 'bbcode_container')
				innerquote.extract() # don't need quote contents
			else: quotedUsername = None
			
			# i don't remember what this does lol
			if username == 'Mafia Host':
				content = post.find('blockquote', class_ = 'postcontent')
			else:
				content = cleanText(post.find('blockquote', class_ = 'postcontent').text)

			# construct post representation
			postArrItem = [int(postnum[1:]), username, quotedUsername, content]

			pagePostsArr.append(postArrItem)

		return pagePostsArr

class ThreadScraper:
	def __init__(self, startUrl):
		self.url = startUrl
		print(f"Starting game: {self.url} ...")

	def scrape(self):
		""" concatenates all individual page arrays
		to form a thread array. """

		threadPostsArr = []

		while self.url: # while next page exists
			pageScraper = PageScraper(self.url)
			scraped = pageScraper.scrape()
			threadPostsArr += scraped
			nextUrl = pageScraper.getNextUrl()
			self.url = nextUrl # None if on final page

		# breaking up printout for when we scrape a list of threads	
		print("\n")

		return threadPostsArr
