import json,platform,logging,os,sys
from authorization import oauth_login
from search_tweets import twitter_search, harvest_user_timeline, save_time_series_data, get_and_save_tweets_form_stream_api,twitter_trends
from functools import partial
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from AnalysisModule.analyze_tweets import  get_common_tweet_entities, extract_tweet_entities,print_prettytable

logger = logging.getLogger(__name__)
#to print info messages debug must be true!
debug = True


def debug_print(message):
    """
    Prints messages if the debug variable is set to true
    :param message: message to be printed
    :return: none
    """""
    if debug:
        print >> sys.stderr, "INFO: ", message
        print >> sys.stderr.flush()

def setup_logging():
    """
    Initializing the logging system used to write errors to a log file
    """
   #ceating a file handler
    #logger.level(logging.INFO)
    if platform.system() == 'Windows':
        LOG_FILE = os.path.expanduser("C:/Users/Windows/Desktop/twitterAnalyzer/CrawlingModule/Resources/error.log").replace("\\", "/")
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
        action = None
        while not action:
            print "Type the number of the action you want to be executed: "
            print "1. Find the trending topics in the world"
            print "2. Search & save trending topics on 15 seconds"
            print "3. Search a limited number of tweets for a specific query "
            print "4. Search & save tweets for a specific query"
            print "5. Search & save tweets from the streaming api"
            print "6. Load tweets from the database for a specific query"
            print "7. Get tweets for specific user account"
            print "8. Analyze entities"
            print "9. Print analysis with pretty table"
            action = raw_input('Enter the number of the action: ').strip()
        WORLD_WOE_ID = 1
        if action == '1':
            #print trending topics
            print "INFO: Getting World Trends ..."

            world_trends = twitter_trends(api, WORLD_WOE_ID)
            #for checking the structure of uncomment : #print json.dumps(world_trends[0]['trends'], indent=1)
            if world_trends:
                world_trends = world_trends[0]['trends']
                for w in world_trends:
                    print "trend: ", w['name']

        elif action == '2':
            #making a partial class from twitter_search to later add it as an argument in save_time_series_data
            trending_topics = partial(twitter_trends, api, WORLD_WOE_ID)
            #get and save the trending topics
            save_time_series_data(trending_topics, 'twitter', '#trends')

        elif action == '3' or action == '4' or action == '5' or action == '6':
            q = None
            print "Read How to build a query first ! ( https://dev.twitter.com/docs/using-search )  "
            q = raw_input('Enter a query: ').strip()
            while not q:
                q = raw_input('Enter a query:').strip()

            if action == '3':
                results = twitter_search(api, q, max_results=10)

                #check if results for that query are found
                if debug: # Show one sample search result by slicing the list...
                    print "Result: ", json.dumps(results[0], indent=1)
                    print >> sys.stderr, "INFO: Count for query:\'", q, "\'  is: ", len(results)
                    print >> sys.stderr.flush()

            if action == '4':
                if debug:
                    print "INFO: Searching tweets for the query:", q
                #search_tweets = partial(twitter_search, api, q, 10000)
                #save_time_series_data(search_tweets, 'twitter', q)
                results = twitter_search(api, q, 1000)
                if debug:
                    print "INFO: Tweets saved into database"

            if action == '5':
                if debug:
                    print "INFO: Searching and saving tweets from the streaming api for query: ", q, "..."
                get_and_save_tweets_form_stream_api(api, q)

            if action == '6':
                if debug:
                    print "INFO: Getting data from database for query: ", q, " ... "

                from_mongo = load_from_mongo("twitter", q)
                if not from_mongo:
                    print "No data for query: ", q
                print "Number of results from this query: ", q, " is: ", len(from_mongo)

        elif action == '7':
                screen_name = raw_input('Enter the screen name: ').strip()
                while not screen_name:
                    screen_name = raw_input('Enter a query:').strip()
                if debug:
                    print "INFO: Getting tweets from user: ", screen_name, " ... "
                tweets = harvest_user_timeline(api, screen_name="SocialWebMining", max_results=200)
                save_to_mongo(tweets, "twitter", screen_name)
        elif action == '8':
                results = load_from_mongo("twitter","#indyref")
                get_common_tweet_entities(results)
        elif action == '9':
                results = load_from_mongo("twitter","#indyref")
                common_entities = get_common_tweet_entities(results)
                print_prettytable(common_entities)

        else:
            print "WRONG ACTION!!!"
    else:
        print "You are not authorized!!!"
if __name__ == '__main__':
    main()




