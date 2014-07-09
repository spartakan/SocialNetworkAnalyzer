import logging
import os
import platform
import pymongo
import datetime
import time
import sys
import json
import twitter
from urllib2 import URLError
from httplib import BadStatusLine



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


def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):
# A nested helper function that handles common HTTPErrors. Return an updated
# value for wait_period if the problem is a 500 level error. Block until the
# rate limit is reset if it's a rate limiting issue (429 error). Returns None
# for 401 and 404 errors, which requires special handling by the caller.

    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e
        # See https://dev.twitter.com/docs/error-codes-responses for common codes
        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429:
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e
    # End of nested helper function
    wait_period = 2
    error_count = 0
    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise



def twitter_trends(twitter_api, woe_id):
    """
    Returns the top 10 trending topics for a specific WOEID, if trending information is available for it
    """
    # Prefix ID with the underscore for query string parameterization.
    # Without the underscore, the twitter package appends the ID value
    # to the URL itself as a special-case keyword argument.
    return twitter_api.trends.place(_id=woe_id)


def twitter_search(twitter_api, q, max_results=1000, **kw):
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
        print>> sys.stderr, 'INFO: Executing twitter_search() method ...  '
        print >> sys.stderr.flush()

    #Get a collection of relevant Tweets matching a specified query
    try:
        search_results = twitter_api.search.tweets(q=q, count=1000, **kw)
        statuses = search_results['statuses']
        if debug:
            print >> sys.stderr, "INFO : number of statuses: ", len(statuses), "max_limit: ", max_results
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
        print>> sys.stderr, "INFO : Executing save_to_mongo() method ..."
        print >> sys.stderr.flush()

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
    """
    Loads data from the specific database and the specific collection by the chosen criteria
    :param mongo_db
    :param mongo_db_coll
    :param return_cursor
    :param criteria
    :param projection
    :param mongo_conn_kw
    """
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
        print >> sys.stderr, "Writing {0} trends to database ".format(len(ids))
        print >> sys.stderr, "wait for 15 seconds ..."
        print >> sys.stderr.flush()

        time.sleep(secs_per_interval)  # seconds
        interval += 1
        print "interval", interval
        if interval >= 15:
             break

def save_tweets_form_stream_api(twitter_api, q):

    twitter_stream = twitter.TwitterStream(auth=twitter_api.auth)
    # See https://dev.twitter.com/docs/streaming-apis
    stream = twitter_stream.statuses.filter(track=q)

    for tweet in stream:
        #print tweet['text']
        save_to_mongo(tweet, "twitter", q)

def harvest_user_timeline(twitter_api, screen_name=None, user_id=None, max_results=1000):
    assert (screen_name != None) != (user_id != None), \
        "Must have screen_name or user_id, but not both"
    kw = {# Keyword args for the Twitter API call
        'count': 200,
        'trim_user': 'true',
        'include_rts' : 'true',
        'since_id' : 1
        }
    if screen_name:
        kw['screen_name'] = screen_name
    else:
        kw['user_id'] = user_id
    max_pages = 16
    results = []
    tweets = make_twitter_request(twitter_api.statuses.user_timeline, **kw)

    if tweets is None: # 401 (Not Authorized) - Need to bail out on loop entry
        tweets = []

    results += tweets
    print >> sys.stderr, 'Fetched %i tweets' % len(tweets)
    page_num = 1

    if max_results == kw['count']:
        page_num = max_pages # Prevent loop entry

    while page_num < max_pages and len(tweets) > 0 and len(results) < max_results:
        # Necessary for traversing the timeline in Twitter's v1.1 API:
        # get the next query's max-id parameter to pass in.
        # See https://dev.twitter.com/docs/working-with-timelines.
        kw['max_id'] = min([tweet['id'] for tweet in tweets]) - 1
        tweets = make_twitter_request(twitter_api.statuses.user_timeline, **kw)
        results += tweets
        print >> sys.stderr, 'Fetched %i tweets' % (len(tweets))
        page_num += 1
    print >> sys.stderr, 'Done fetching tweets'
    return results[:max_results]