import sys, os, platform
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from debugging_setup import debug_print

print "Execution 1"

def find_popular_tweets(retweet_threshold=3):
    """ You could also consider using the favorite_count parameter as part of
        this heuristic, possibly using it to provide an additional boost to
        popular tweets in a ranked formulation  """
    debug_print("Executing find popular tweets ... ")

    #get tweets from database
    criteria = {"retweet_count": {"$gt": 400}}
    projection = {"_id": 1, "retweet_count": 1, "favorite_count":1 , "text":1}
    tweets = load_from_mongo("twitter", "#indyref", criteria=criteria, projection=projection)
    for tweet in tweets:
        print "retweet_count: ", tweet['retweet_count'], " favorite_count: ", tweet['favorite_count']
        weight = 0
        weight = tweet['retweet_count'] * 0.01
        weight = weight+ tweet['favorite_count']*0.01
        print " "
        print tweet['text'], " [  weight  :  ", weight, " ]"

        if weight > retweet_threshold:
            print "valid tweet : ", tweet['_id']

find_popular_tweets()