# Hava Parker - COM528 Final Project

import argparse
from scraper import *
from threadAnalyzer import *

def analyzeThreads(threadListFile):
	threadList = open(threadListFile)
	threads = threadList.readlines()

	allAverages = {}
	allAverages['w'] = {}
	allAverages['v'] = {}

	allAverages['w']['postcountPercent'] = []
	allAverages['w']['wordsPerPost'] = []
	allAverages['w']['wolfInteractionPercent'] = []

	allAverages['v']['postcountPercent'] = []
	allAverages['v']['wordsPerPost'] = []
	allAverages['v']['wolfInteractionPercent'] = []

	output = open("perThread-Mixed.txt", 'a')

	for thread in threads:
		try:
			scraper = ThreadScraper(thread)
			postArr = scraper.scrape()
			analyzer = ThreadAnalyzer(postArr)

			analyzer.trimThread()
			endPost = str(analyzer.posts[-1][3])

			try:
				try:
					analyzer.getRoster(endPost)
				except UnboundLocalError:
						print("err 1")
						print(endPost)
						endPost = str(analyzer.posts[-2][3])
						analyzer.posts = analyzer.posts[:-1]
						analyzer.getRoster(endPost)
			except UnboundLocalError:
				print("err 2")
				endPost = str(analyzer.posts[-3][3])
				analyzer.posts = analyzer.posts[:-2]
				analyzer.getRoster(endPost)

			analyzer.traversePosts()

			threadSummary = summarizeThread(analyzer)
			allAverages['w']['postcountPercent'].append(threadSummary['w']['postcountPercent'])
			allAverages['w']['wordsPerPost'].append(threadSummary['w']['wordsPerPost'])
			allAverages['w']['wolfInteractionPercent'].append(threadSummary['w']['wolfInteractionPercent'])
			
			allAverages['v']['postcountPercent'].append(threadSummary['v']['postcountPercent'])
			allAverages['v']['wordsPerPost'].append(threadSummary['v']['wordsPerPost'])
			allAverages['v']['wolfInteractionPercent'].append(threadSummary['v']['wolfInteractionPercent'])

			output.write(thread)
			output.write("---------")
			output.write(str(threadSummary))
			output.write("---------")
			for poster in analyzer.roster:
				output.write(str(poster) + "\n")
			output.write("\n\n")
		except Exception as e:
			print("Last attempt on thread " + thread + f". Exception {e} encountered.")

	output.close()

	return allAverages

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('threadList')
	args = parser.parse_args()

	output = open("analysis-Mixed", 'w')
	output.write(str(analyzeThreads(args.threadList)))
	output.close()

if __name__ == "__main__":
    main()

# {'baseline': 20.0, 
# 'w': {'postcount': 201, 'wordcount': 28.62, 'wolfInteractionPercent': 10.74},
# 'v': {'postcount': 197.17, 'wordcount': 19.72, 'wolfInteractionPercent': 19.06}}