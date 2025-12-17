# Hava Parker - COM528 Final Project

import argparse
from scraper import *
from threadAnalyzer import *

def analyzeThreads(args):
	""" Analyzes a set of threads and reports three
	figures:
	1. average faction member postcount
	2. average faction member's words per post
	3. average faction member's interaction w/mafia rate

	Produces two reports, written to separate files:
	1. information by thread
	2. averaged information by thread (i.e.,
	data on the full set of threads)
	"""

	threadList = open(args.threadList)
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

	perThreadOutput = open(args.perThreadOutput, 'a')

	for thread in threads:
		try:
			scraper = ThreadScraper(thread)
			postArr = scraper.scrape()
			analyzer = ThreadAnalyzer(postArr)

			analyzer.trimThread()

			# game-over post is the final post in
			# the trimmed thread
			endPost = str(analyzer.posts[-1][3])

			# ... but MU inconsistencies possible,
			# need to rewrite this for accuracy
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
			output.write("---------\n")
			output.write(str(threadSummary))
			output.write("---------\n")
			for poster in analyzer.roster:
				output.write(str(poster) + "\n")
			output.write("\n\n")
		except Exception as e:
			print("Last attempt on thread " + thread + f". Exception {e} encountered.")

	summaryOutput = open(args.summaryOutput, 'w')
	summaryOutput.write(str(allAverages))
	summaryOutput.close()

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--threadList', '-t')
	parser.add_argument('--perThreadOutput', '-o')
	parser.add_argument('--summaryOutput', '-s')
	args = parser.parse_args()

	analyzeThreads(args)

	# fix this so we don't need to hardcode filenames
	
	# output = open("analysis-Mixed", 'w')
	# output.write(str(analyzeThreads(args.threadList)))
	# output.close()

if __name__ == "__main__":
    main()