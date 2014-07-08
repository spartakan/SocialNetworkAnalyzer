import json
import platform
import logging
import os
import sys
sys.path.append(os.path.abspath("H:/twitterAnalyzer/CrawlingModule"))
from authorization import oauth_login
from search_tweets import twitter_search, save_to_mongo, load_from_mongo, save_time_series_data, save_tweets_form_stream_api,twitter_trends
from functools import partial

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

        q = None
        q = raw_input('Enter a query: ').strip()
        while not q:
            q = raw_input('').strip()
        if q:
            results = twitter_search(api, q, max_results=10)

            #test trending topics
            print "INFO: Getting World Trends ..."
            WORLD_WOE_ID = 1
            #world_trends = twitter_trends(api, WORLD_WOE_ID)
            #print json.dumps(world_trends[0]['trends'], indent=1)
            #if world_trends:
                #world_trends= world_trends[0]['trends']
                #for w in world_trends:
                    #print "trend: ", w['name']


            #making a partial class from twitter_search to later add it as an argument in get_time_series_data
            #trending_topics = partial(twitter_trends, api,WORLD_WOE_ID)


            #get and save the trending topics
            #save_time_series_data(trending_topics, 'twitter', '#trends')

            #if results:
                #save_to_mongo(results, "twitter", q)


            #check if results for that query are found
            if debug: # Show one sample search result by slicing the list...
                #print "Result: ", json.dumps(results[0], indent=1)
                print "INFO: Count for query( \'", q, "\' ) : ", len(results)

                print "INFO: Getting data from database for query: ", q, " ... "
                from_mongo = load_from_mongo("twitter", q)
                if from_mongo:
                    for item in from_mongo:
                        print item
                else:
                    print "No data for query: ", q

            #    print "INFO: Getting tweets from streaming api for query : ", q
            #    save_tweets_form_stream_api(api, q)

            else:
                print "INFO: No results for :", q

if __name__ == '__main__':
    main()




