import requests
from bs4 import BeautifulSoup

headers = requests.utils.default_headers()
headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
})

posters = {}

def scrapePage(url, isFirstPage = False): 
	page = requests.get(url, headers=headers)
	soup = BeautifulSoup(page.content, 'html.parser')

	paginator = soup.find("div", id="pagination_top")
	nextPageExists = paginator.find("img", alt="Last")
	if isFirstPage: print("yes")

	postlist = soup.find(id = 'posts') # find <ol>
	posts = postlist.find_all(attrs = {'data-postnumber': True}) # full post square, incl head/ftr

	if isFirstPage:
		moderatorUsername = posts[0].find("a", class_ = "username").text

	f = open("posts.html", 'a')

	for post in posts:
		pnum = post.find("a", class_ = "postcounter").text
		username = post.find("a", class_="username").text
		quoteExists = post.find("div", class_="bbcode_postedby")
		if quoteExists:
			quoted = post.find("div", class_="bbcode_postedby").find("strong")
			innerquote = post.find("div", class_="bbcode_container")
			innerquote.extract()
		content = post.find("blockquote", class_ = "postcontent").text
		contentLength = len(content.split())

		if username == "Mafia Host": continue

		if username not in posters:
			posters[username] = {}
			posters[username]["postcount"] = 1
			posters[username]["wordcount"] = contentLength
		else:
			posters[username]["postcount"] += 1
			posters[username]["wordcount"] += contentLength

		f.write(pnum + ": " + username + "\n")
		if quoteExists: f.write("Quoted: " + quoted.text + "\n")
		f.write(content.strip())
		f.write("\n---\n")
	f.close()

	print(posters)

	if nextPageExists:
		print("next exists")
		currentPage = url[-1]
		nextPage = int(currentPage) + 1
		nextPageUrl = url[:-1] + str(nextPage)
		# scrapePage(nextPageUrl, moderatorUsername)

def scrapeThread(startUrl):
	scrapePage(startUrl, True)

scrapePage("https://www.mafiauniverse.com/forums/threads/44128-Eel-Appreciation-Mafia-(Mountainous)/page2")
