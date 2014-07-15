import logging,datetime,json,time,sys,twitter,urllib2
from urllib2 import URLError
from httplib import BadStatusLine
from functools import partial
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from debugging_setup import setup_logging, debug_print

logger = setup_logging()


def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):
    """ A nested helper function that handles common HTTPErrors. Return an updated
    value for wait_period if the problem is a 500 level error. Block until the
    rate limit is reset if it's a rate limiting issue (429 error). Returns None
    for 401 and 404 errors, which requires special handling by the caller.
    USED in: all functions that make a call to the twitter api
    """

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
        elif e.e.code in (500, 502, 503, 504, 104):  #104 is for socket error : connection reset by peer
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
    Returns the top 10 trending topics for a specific WOEID, if trending information is available for it.
    For preventing HTTP errors a robust API wrapper is added
    """
    # Prefix ID with the underscore for query string parameterization.
    # Without the underscore, the twitter package appends the ID value
    # to the URL itself as a special-case keyword argument.
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

    debug_print('Executing twitter_search() method ...  ')
    #Get a collection of relevant Tweets matching a specified query

    try:
        twitter_search_api_tweets = partial(twitter_api.search.tweets, q=q, count=180, **kw)
        search_results = make_twitter_request(twitter_search_api_tweets)

    #Handle rate limit
    except urllib2.HTTPError, e:
            if e.e.code == 429 or e.e.code == 420: #rate limit reached
                 #find the highest since_id from database to continue if a rate limitation is reached
                since_id = load_from_mongo('twitter', q, return_cursor=False, find_since_id=True)
                if since_id:
                    debug_print(" since_id: "+ str(since_id))
                    kw = {'since_id': since_id}
                    twitter_search(twitter_api, q, **kw)
                else:
                    print "No since_id"
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 10)
    statuses = search_results['statuses']
    debug_print("number of statuses: " + str(len(statuses)) + " max_limit: " + str(max_results))

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
            debug_print("BREAK: next_results: " + str(len(search_results['statuses'])))
            break
        debug_print("results: " + next_results)
        kwargs = dict([kv.split('=') for kv in next_results[1:].split("&")])
        kwargs['result_type'] = "recent"
        debug_print("kwargs: "+str(kwargs))
        twitter_search_api_tweets = partial(twitter_api.search.tweets, **kwargs)
        search_results = make_twitter_request(twitter_search_api_tweets)
        debug_print("number of statuses: " + str(len(search_results['statuses'])))
        statuses += search_results['statuses']
        debug_print("B: length statuses: " + str(len(statuses)))
        #print json.dumps(search_results,indent=1)
        #break
        if len(statuses) > max_results:
           debug_print("BREAK: statuses: " +  str(len(statuses)))
           break
    if statuses:
        debug_print(('Saving %d statsus')%len(statuses))
    for tweet in statuses:
        #print json.dumps(tweet, indent=1)
        save_to_mongo(tweet, "twitter", q)





def save_time_series_data(api_func, mongo_db_name, mongo_db_coll, secs_per_interval=60, max_intervals=15, **mongo_conn_kw):
    """
    On every 15 seconds executes an api function that makes a call to the Twitter api.
    This way it prevents reaching the api's rate limit.
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
        ids = save_to_mongo(api_func(), mongo_db_name, mongo_db_coll)
        print >> sys.stderr, "Writing {0} trends to database ".format(len(ids))
        print >> sys.stderr, "wait for 15 seconds ... "
        print >> sys.stderr.flush()

        time.sleep(secs_per_interval)  # seconds
        interval += 1
        print "interval", interval
        if interval >= 15:
            break

def get_and_save_tweets_form_stream_api(twitter_api, q):

    """
    Uses twitter's Streaming API to get samples of the public data flowing through tweeter.
    Establishes a connection to a streaming endpoint they are delivered a feed of Tweets,
    without needing to worry about polling or REST API rate limits.
    For preventing HTTP errors a robust API wrapper is added
    """
    twitter_stream = partial(twitter.TwitterStream, auth=twitter_api.auth)
    twitter_stream = make_twitter_request(twitter_stream)
    # See https://dev.twitter.com/docs/streaming-apis
    stream = twitter_stream.statuses.filter(track=q)
    for tweet in stream:
        #print json.dumps(tweet, indent=1)
        save_to_mongo(tweet, "twitter", q)



def harvest_user_timeline(twitter_api, screen_name=None, user_id=None, max_results=1000):
    """
    Harvest all of user's most recent tweets. Number of retrieved tweets can grow to 3,200
    so a robust API wrapper is added
    """
    assert (screen_name != None) != (user_id != None), \
        "Must have screen_name or user_id, but not both"

    kw = { # Keyword args for the Twitter API call
        'count': 200,
        'trim_user': 'true',
        'include_rts': 'true',
        'since_id': 1
        }
    if screen_name:
        kw['screen_name'] = screen_name
    else:
        kw['user_id'] = user_id
    max_pages = 16
    results = []
    tweets = make_twitter_request(twitter_api.statuses.user_timeline, **kw)

    if tweets is None:# 401 (Not Authorized) - Need to bail out on loop entry
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