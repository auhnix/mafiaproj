# Hava Parker - COM528 Final Project

import argparse, random, requests, time
from bs4 import BeautifulSoup

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
		page = requests.get(url, headers = headers)
		self.soup = BeautifulSoup(page.content, 'html.parser')
		self.postlist = self.soup.find(id = 'posts')
		self.posts = self.postlist.find_all(attrs = {'data-postnumber': True})

	def cleanText(self, text):
		cleanedText = ' '.join(text.split())
		return cleanedText

	def getNextUrl(self):
		paginator = self.soup.find('div', id = 'pagination_top')
		prevNexts = paginator.find_all('span', class_ = 'prev_next')
		nextUrl = None
		for prevNext in prevNexts:
			if prevNext.find('a', {'rel': 'next'}):
				nextUrl = self.baseUrl + prevNext.find('a', {'rel': 'next'})['href']
		return nextUrl

	def scrapeLegacy(self, output):
		for post in self.posts:
			checkPostValid = post.find('a', class_ = 'postcounter')
			if checkPostValid:
				postnum = post.find('a', class_ = 'postcounter').text
			else:
				output.write("*** idk what's happening! ***\n\n")
				output.write(post.prettify())
				output.write("*** idk what's happening! ***\n\n")
				continue
			username = post.find('a', class_ = 'username').text
			if username in self.ignoredPosters:
				continue

			quoteExists = post.find('div', class_ = 'bbcode_postedby')
			if quoteExists:
				quotedUsername = post.find('div', class_ = 'bbcode_postedby').find('strong').text
				innerquote = post.find('div', class_ = 'bbcode_container')
				innerquote.extract() # don't need quote contents
			content = post.find('blockquote', class_ = 'postcontent').text
			contentLength = len(content.split())

			output.write(postnum + ": " + username + "\n")
			if quoteExists: output.write("Quoted: " + quotedUsername + "\n")
			output.write(content.strip())
			output.write("\n-----\n")

			storedPoster = self.findPosterByUsername(username)
			if storedPoster:
				storedPoster.updateCounts(contentLength)
				if quoteExists and quotedUsername != username:
					storedPoster.updateInteractions(quotedUsername)
			else:
				newPoster = Poster(username, 1, contentLength)
				self.posters.append(newPoster)
				if quoteExists and quotedUsername != username:
					newPoster.updateInteractions(quotedUsername)

	def scrape(self):
		pagePostsArr = []

		for post in self.posts:
			checkPostValid = post.find('a', class_ = 'postcounter')
			if checkPostValid:
				postnum = post.find('a', class_ = 'postcounter').text
			else:
				continue

			username = post.find('a', class_ = 'username').text
			quoteExists = post.find('div', class_ = 'bbcode_postedby')

			if quoteExists:
				quotedUsername = post.find('div', class_ = 'bbcode_postedby').find('strong').text
				innerquote = post.find('div', class_ = 'bbcode_container')
				innerquote.extract() # don't need quote contents
			else: quotedUsername = None
			
			if username == 'Mafia Host':
				content = post.find('blockquote', class_ = 'postcontent')
			else:
				content = self.cleanText(post.find('blockquote', class_ = 'postcontent').text)

			postArrItem = [int(postnum[1:]), username, quotedUsername, content]

			pagePostsArr.append(postArrItem)

		return pagePostsArr

class ThreadScraper:
	def __init__(self, startUrl):
		self.url = startUrl
		print(f"Starting game: {self.url} ...")

	def scrape(self):
		threadPostsArr = []

		while self.url:
			pageScraper = PageScraper(self.url)
			scraped = pageScraper.scrape()
			threadPostsArr += scraped
			nextUrl = pageScraper.getNextUrl()
			self.url = nextUrl
		print("\n")
		return threadPostsArr
