import json
import platform
import logging
import os
import sys
sys.path.append(os.path.abspath("H:/twitterAnalyzer/CrawlingModule"))
from authorization import oauth_login
from search_tweets import twitter_search, save_to_mongo


logger = logging.getLogger(__name__)
#to print info messages debug must be true!
debug = True

def setup_logging():
    """
    Initializing the logging system used to write errors to a log file
    """
    #ceating a file handler
    #logger.level(logging.INFO)
    if platform.system() == 'Windows':
        LOG_FILE = os.path.expanduser("H:/twitterAnalyzer/CrawlingModule/Resources/error.log").replace("\\", "/")
    elif platform.system() == 'Linux':
        LOG_FILE = os.path.abspath(os.path.expanduser("~/twitterAnalyzer/CrawlingModule/Resources/error.log"))
    handler = logging.FileHandler(LOG_FILE)
    handler.setLevel(logging.ERROR)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)


def main():
    setup_logging()
    api = oauth_login()

    if api:
        if debug:
            print "INFO: Successfully authenticated and authorized"
            print "Read How to build a query first ! ( https://dev.twitter.com/docs/using-search )  "
        q = raw_input('Enter a query: ').strip()
        results = twitter_search(api, q, max_results=10)
        save_to_mongo(results,"twitter",q)
        #check if results for that query are found
        if results and debug: # Show one sample search result by slicing the list...
            print "Result: ", json.dumps(results[0], indent=1)
            print "INFO: Count for query( \'", q, "\' ) : ", len(results)
        else:
            print "INFO: No results for :", q

if __name__ == '__main__':
    main()




