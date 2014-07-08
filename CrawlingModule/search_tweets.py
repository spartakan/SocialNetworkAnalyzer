import logging
import os
import platform
import pymongo
import datetime
import time
import sys
import twitter

#to print info messages debug must be true!
debug = True
logger = logging.getLogger(__name__)

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


#setup the logger with proper handler
setup_logging()

def twitter_trends(twitter_api, woe_id):
    """
    Returns the top 10 trending topics for a specific WOEID, if trending information is available for it
    """
    # Prefix ID with the underscore for query string parameterization.
    # Without the underscore, the twitter package appends the ID value
    # to the URL itself as a special-case keyword argument.
    return twitter_api.trends.place(_id=woe_id)


def twitter_search(twitter_api, q, max_results=200, **kw):
    """
    Search tweets for a given query
    description of parametars: https://dev.twitter.com/docs/api/1.1/get/search/tweets
    Warning: OAuth users can "only" make 180 search queries per 15-minute interval.
     :param twitter_api
     :param q
     :param max_results
     :param kw
     """
    if debug:
        print 'INFO: Executing twitter_search() method ...  '

    #Get a collection of relevant Tweets matching a specified query
    try:
        search_results = twitter_api.search.tweets(q=q, count=100, **kw)
        statuses = search_results['statuses']
        if debug:
            print "INFO : number of statuses: ", len(statuses)
    except Exception, e:
        logger.error('Failed request', exc_info=True)
        return False

    else:
        max_results = min(1000, max_results)
        # Iterate through 5 more batches of results by following the cursor
        for _ in range(10):  # 10*100 = 1000
            try:
                next_results = search_results['search_metadata']['next_results']
            except KeyError, e:
                logger.error('Failed to find attribute '
                             + '(WARRNING: might throw this exception '
                             + 'for some results while searching in the loop)'
                             , exc_info=True)
                break
            kwargs = dict([kv.split('=') for kv in next_results[1:].split("&")])
            search_results = twitter_api.search.tweets(**kwargs)
            statuses += search_results['statuses']
            if len(statuses) > max_results:
                break
        return statuses


def save_to_mongo(data, mongo_db, mongo_db_coll, **mongo_conn_kw):
    if debug:
        print "INFO : Saving to database ..."

    # Connects to the MongoDB server running on
    # localhost:27017 by default
    client = pymongo.MongoClient(**mongo_conn_kw)

    # Get a reference to a particular database
    db = client[mongo_db]
    # Reference a particular collection in the database
    coll = db[mongo_db_coll]
    # Perform a bulk insert and return the IDs
    return coll.insert(data)






def load_from_mongo(mongo_db, mongo_db_coll, return_cursor=False, criteria=None, projection=None, **mongo_conn_kw):
    # Optionally, use criteria and projection to limit the data that is
    # returned as documented in
    # http://docs.mongodb.org/manual/reference/method/db.collection.find/

    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]
    if criteria is None:
        criteria = {}
    if projection is None:
        cursor = coll.find(criteria)
    else:
        cursor = coll.find(criteria, projection)
        # Returning a cursor is recommended for large amounts of data
    if return_cursor:
        return cursor
    else:
        return [item for item in cursor]


def save_time_series_data(api_func, mongo_db_name, mongo_db_coll,
                         secs_per_interval=60, max_intervals=15, **mongo_conn_kw):
    """
    Calls the Twitter api on every 15 seconds, usually used to see what topics are trending at the moment
    and saves them into database
    :param api_func
    :param mongo_db_name
    :param mongo_db_coll
    :param secs_per_interval
    :param max_intervals
    :param mongo_conn_kw
    """
    # Default settings of 15 intervals and 1 API call per interval ensure that
    # you will not exceed the Twitter rate limit.
    interval = 0
    while True:
        # A timestamp of the form "2013-06-14 12:52:07"
        now = str(datetime.datetime.now()).split(".")[0]
        ids = save_to_mongo(api_func(), mongo_db_name, mongo_db_coll + "-" + now)
        print >> sys.stderr, "Write {0} trends".format(len(ids))
        print >> sys.stderr, "Zzz..."
        print >> sys.stderr.flush()
        time.sleep(secs_per_interval) # seconds
        interval += 1
        if interval >= 15:
            break

def save_tweets_form_stream_api(twitter_api, q):

    twitter_stream = twitter.TwitterStream(auth=twitter_api.auth)
    # See https://dev.twitter.com/docs/streaming-apis
    stream = twitter_stream.statuses.filter(track=q)

    for tweet in stream:
        print tweet['text']
        save_to_mongo(tweet, "twitter", q)
    # Save to a database in a particular collection