
from authorization import oauth_login
from search_tweets import twitter_search, harvest_user_timeline, save_time_series_data, get_and_save_tweets_form_stream_api,twitter_trends
from get_list import get_list_memebers
from functools import partial
import sys
import platform
import os
if platform.system() == 'Linux':
    sys.path.insert(0,os.path.abspath("/home/sd/twitterAnalyzer"))
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from AnalysisModule.analyze_tweets import get_common_tweet_entities,extract_tweet_entities,print_prettytable
from debugging_setup import setup_logging, debug_print

def main():
    api = oauth_login()
    setup_logging()


    if api:
        debug_print("Successfully authenticated and authorized")
        action = None
        while not action:
            print "Type the number of the action you want to be executed: "
            print "1. Find the trending topics in the world"
            print "2. Search & save trending topics on 15 seconds"
            print "3. Get list members"
            print "4. Search & save tweets for a specific query"
            print "5. Search & save tweets from the streaming api"
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
        elif action == '3':
            get_list_memebers(api)
        elif action == '4' or action == '5' :
            q = None
            print "Read How to build a query first ! ( https://dev.twitter.com/docs/using-search )  "
            q = raw_input('Enter a query: ').strip()
            while not q:
                q = raw_input('Enter a query:').strip()
            if action == '4':
                debug_print("Searching tweets for the query:" + q)
                #search_tweets = partial(twitter_search, api, q, 10000)
                #save_time_series_data(search_tweets, 'twitter', q)
                results = twitter_search(api, q, 1000)
                debug_print("Tweets saved into database")

            if action == '5':
                debug_print("Searching and saving tweets from the streaming api for query: " +q+ "...")
                get_and_save_tweets_form_stream_api(api, q)

        elif action == '7':
                screen_name = raw_input('Enter the screen name: ').strip()
                while not screen_name:
                    screen_name = raw_input('Enter a query:').strip()
                debug_print("Getting tweets from user: "+ screen_name+ " ... ")
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




