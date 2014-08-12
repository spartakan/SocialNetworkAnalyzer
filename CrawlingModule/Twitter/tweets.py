import datetime,json,time,twitter
import urllib2
from urllib2 import URLError
from httplib import BadStatusLine
from functools import partial
from config import *
from DatabaseModule.TwitterWrapper.database_manipulation_twitter import save_to_mongo_twitter
from DatabaseModule.database_manipulation import load_from_mongo
from socket import error as SocketError
from twitter.api import TwitterHTTPError

logger = logging.getLogger(__name__)
logger = setup_logging(logger)



def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):
    """ A nested helper function that handles common HTTPErrors. Return an updated
    value for wait_period if the problem is a 500 level error. Block until the
    rate limit is reset if it's a rate limiting issue (429 error). Returns None
    for 401 and 404 errors, which requires special handling by the caller.
    USED in: all functions that make a call to the twitter api
    """
    debug_print('EXEC make_twitter_request method : ')
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            logger.error(e.message)
            raise e
        # See https://dev.twitter.com/docs/error-codes-responses for common codes
        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            logger.error(e.message)
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            logger.error(e.message)
            return None
        elif e.e.code == 420:
            print  'Encountered 420 Error (Rate Limit Exceeded)'
            logger.error(e)
            if sleep_when_rate_limited:
                debug_print("  Rate limit reached. Start:" + str(time.ctime()) + " . Retrying in 15 min ...zZz...")
                logger.error(e.message)
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                debug_print("  Woke up ... End: " + str(time.ctime()))
                logger.error(e.message)
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504, 104):  #104 is for socket error : connection reset by peer
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % (e.e.code, wait_period)
            logger.error(e.message)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            print " -- else : ", e.message
            raise e
    # End of nested helper function
    wait_period = 2
    error_count = 0
    while True:
        try:
            return twitter_api_func(*args, **kw)
        except TwitterHTTPError, e:
            logger.error(e.message)
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            logger.error(e.message)
            error_count += 1
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            logger.error(e.message)
            error_count += 1
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise




def twitter_trends(twitter_api, woe_id):
    """
    Returns the top 10 trending topics for a specific WOEID, if trending information is available for it.
    For preventing HTTP errors a robust API wrapper is added
    """
    # Prefix ID with the underscore for query string parameterization.
    # Without the underscore, the twitter package appends the ID value
    # to the URL itself as a special-case keyword argument.
    debug_print('EXEC twitter_trends method : ')
    twitter_api_trends = partial(twitter_api.trends.place, _id=woe_id)
    make_twitter_request(twitter_api_trends)
    return make_twitter_request(twitter_api_trends)



def twitter_search(twitter_api, q, max_results=1000, **kw):
    """
    Retrieves tweets from the api for a given query
    description of parametars: https://dev.twitter.com/docs/api/1.1/get/search/tweets
    Warning: OAuth users can "only" make 180 search queries per 15-minute interval.
    For preventing HTTP errors a robust API wrapper is added
     :param twitter_api
     :param q
     :param max_results
     :param kw
     """

    debug_print('EXEC twitter_search method : ')
    #Get a collection of relevant Tweets matching a specified query

    try:
        twitter_search_api_tweets = partial(twitter_api.search.tweets, q=q, count=180, **kw)
        search_results = make_twitter_request(twitter_search_api_tweets)

    #Handle rate limit
    except urllib2.HTTPError, e:
        if e.e.code == 429 : #rate limit reached TODO: handle this error  inside methods
             #find the highest since_id from database to continue if a rate limitation is reached
            since_id = load_from_mongo('twitter', q, return_cursor=False, find_since_id=True)
            if since_id:
                debug_print(" since_id: "+ str(since_id))
                kw = {'since_id': since_id}
            else:
                debug_print("  No since_id")
            debug_print("  Rate limit reached. Start:" + str(time.ctime()) + " . Retrying in 15 min ...zZz...")
            sys.stderr.flush()
            time.sleep(60*15 + 10)
            debug_print("  Woke up ... End: " + str(time.ctime()))
            twitter_search(twitter_api, q, **kw)

    except SocketError, se:
        logger.error(se)
        debug_print("  " + se.message)
        since_id = load_from_mongo('twitter', q, return_cursor=False, find_since_id=True)
        debug_print("  SocketError occurred. Start:" + str(time.ctime()) + " . Retrying in 0.05 sec ...zZz...")
        time.sleep(0.05)
        debug_print("  Woke up ... End: " + str(time.ctime()))
        if since_id:
            kw = {'since_id': since_id}
        twitter_search(twitter_api, q, **kw)

    statuses = search_results['statuses']
    debug_print("  number of statuses: " + str(len(statuses)) + " max_limit: " + str(max_results))

    # reach the desired number of results, keeping in mind that OAuth users
    # can "only" make 180 search queries per 15-minute interval. See
    # https://dev.twitter.com/docs/rate-limiting/1.1/limits
    # for details. A reasonable number of results is ~1000, although
    # that number of results may not exist for all queries.
    # Enforce a reasonable limit
    max_results = min(1000, max_results)

    print >> sys.stderr, search_results
    # Iterate through more batches of results by following the cursor
    while True:
        debug_print('*** START LOOP ***')
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError, e:
            logger.error('Failed to find attribute ', exc_info=True)
            debug_print("  BREAK: next_results: " + str(len(search_results['statuses'])))
            break
        debug_print("results: " + next_results)
        kwargs = dict([kv.split('=') for kv in next_results[1:].split("&")])
        kwargs['result_type'] = "recent"
        debug_print("kwargs: "+str(kwargs))
        twitter_search_api_tweets = partial(twitter_api.search.tweets, **kwargs)
        search_results = make_twitter_request(twitter_search_api_tweets)
        debug_print("  number of statuses: " + str(len(search_results['statuses'])))
        statuses += search_results['statuses']
        #print json.dumps(search_results,indent=1)
        #break
        if len(statuses) > max_results:
           debug_print("  BREAK: statuses: " +  str(len(statuses)))
           break
    if statuses:
        debug_print(('  Saving %d statsus')%len(statuses))
    for tweet in statuses:
        #print json.dumps(tweet, indent=1)
        save_to_mongo_twitter(tweet, "twitter", q)





def save_time_series_data(api_func, mongo_db_name, mongo_db_coll, secs_per_interval=60, max_intervals=15, **mongo_conn_kw):
    """
    Executes an api function on a given time-interval if no immediate results are needed.
    Usually needed for checking trending topics.
    :param api_func
    :param mongo_db_name
    :param mongo_db_coll
    :param secs_per_interval
    :param max_intervals
    :param mongo_conn_kw
    """
    debug_print('EXEC save_time_series_data method : ')
    # Default settings of 15 intervals and 1 API call per interval ensure that
    # you will not exceed the TwitterWrapper rate limit.
    interval = 0
    while True:
        # A timestamp of the form "2013-06-14 12:52:07"
        now = str(datetime.datetime.now()).split(".")[0]
        ids = save_to_mongo_twitter(api_func(), mongo_db_name, mongo_db_coll)
        print >> sys.stderr, "Writing {0} trends to database ".format(len(ids))
        print >> sys.stderr, "wait for 15 seconds ... "
        print >> sys.stderr.flush()

        time.sleep(secs_per_interval)  # seconds
        interval += 1
        print "interval", interval
        if interval >= 15:
            break

def twitter_stream_api(twitter_api, q):

    """
    Uses twitter's Streaming API to get samples of the public data flowing through tweeter.
    Establishes a connection to a streaming endpoint they are delivered a feed of Tweets,
    without needing to worry about polling or REST API rate limits.
    For preventing HTTP errors a robust API wrapper is added

    """
    debug_print('EXEC twitter_stream_api method : ')
    twitter_stream = partial(twitter.TwitterStream, auth=twitter_api.auth)

    try:
            twitter_stream_res = make_twitter_request(twitter_stream)
            stream = twitter_stream_res.statuses.filter(track=q)
    except (urllib2.HTTPError, SocketError, TwitterHTTPError, SocketError), e:
            debug_print("  " + e.message)
            #find the highest since_id from database to continue if a rate limitation is reached
            #since_id = load_from_mongo('twitter', q, return_cursor=False, find_since_id=True)
            #debug_print(" since_id: %d " % (since_id + 1))
            #kw = {'since_id': since_id}

            logger.error(e)
            debug_print(e)
            debug_print("  Rate limit reached. Start: %s. Retrying in 15 min ...zZz..."%(str(time.ctime())))
            sys.stderr.flush()
            time.sleep(60*15 + 10)
            debug_print("  Woke up ... End: %s" % (str(time.ctime())))
            twitter_stream_res = make_twitter_request(twitter_stream)
            stream = twitter_stream_res.statuses.filter(track=q)

    else:
        debug_print("  No exceptions ")
        # See https://dev.twitter.com/docs/streaming-apis

        if stream:
            for tweet in stream:
                #print json.dumps(tweet, indent=1)
                save_to_mongo_twitter(tweet, "twitter", q)