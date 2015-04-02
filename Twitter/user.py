from functools import partial
import time
from twitter.api import TwitterHTTPError
from sys import maxint

from config import *

import DB.twitter as DB

import Twitter.tweets as tt

#create a logger for this module , set it up, and use it to write errors to file
logger = logging.getLogger(__name__)
logger = setup_logging(logger)


# DATA FETCH FUNCTIONS

def twitter_get_followers(twitter_api, screen_name=None, followers_limit=None):
    """ Retrieve a list of followers(full information represented as a json file) for a specific user.
        For more information on how the file is structured check https://dev.twitter.com/docs/api/1.1/get/followers/list
    :parameter twitter_api
    :parameter screen_name - The screen name of the user for whom to return results for
    :parameter followers_limit - The maximum number of users to return
    :returns followers - list of followers, each represented as a json object
    """
    debug_print("EXEC twitter_get_followers method :")
    #set the cursor to -1 (first page)
    cursor = -1
    followers = []
    if screen_name is not None:
        while cursor != 0:
            #if the followers' limit is reached return the results
            if followers_limit and len(followers) >= followers_limit:
                break
            try:
                # get the first page with results
                response = twitter_api.followers.list(count=200, screen_name=screen_name, cursor=cursor)
                if response is not None:
                    cursor = response['next_cursor']
                    followers += response['users']
                    debug_print("  users (last response): %d " % (len(response['users'])))
                    debug_print("  total followers: %d" % len(followers))

            except TwitterHTTPError, e:
                debug_print(e)
                sys.stderr.flush()
                logger.error(e)
                debug_print("error_code:%i"%e.e.code)
                if e.e.code == 429:   # rate limit is reached
                    debug_print("  Rate limit reached. Start: %s . Retrying in 15 min ...zZz..." % (str(time.ctime())))
                    time.sleep(60*15 + 10)
                    debug_print("  Woke up ... End: %s" % (str(time.ctime())))
                if e.e.code == 401: # not authorized to see user
                    pass

    return followers


def twitter_get_friends_followers_ids(twitter_api, screen_name=None, user_id=None,
                              friends_limit=maxint, followers_limit=maxint):
    """ Retrieves all the ids of friends and followers for a specific user.
    :parameter twitter_api
    :parameter screen_name - The screen name of the user for whom to return results for.
    :parameter user_id - The ID of the user for whom to return results for.
    :parameter friends_limit
    :parameter followers_limit
    :returns friends_ids, followers_ids - lists of friends ids and followers ids
    """
    debug_print("EXEC twitter_get_friends_followers_ids method :")
    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None), \
    "Must have screen_name or user_id, but not both"

    # See https://dev.twitter.com/docs/api/1.1/get/friends/ids and
    # https://dev.twitter.com/docs/api/1.1/get/followers/ids for details
    # on API parameters

    get_friends_ids = partial(twitter_api.friends.ids, count=5000)
    get_followers_ids = partial(twitter_api.followers.ids, count=5000)

    friends_ids, followers_ids = [], []

    for twitter_api_func, limit, ids, label in [
                    [get_friends_ids, friends_limit, friends_ids, "friends"],
                    [get_followers_ids, followers_limit, followers_ids, "followers"]
                ]:

        if limit == 0:
            continue

        cursor = -1
        while cursor != 0:

            # Use twitter_make_robust_request via the partially bound callable...
            try:
                if screen_name:
                    response = twitter_api_func(screen_name=screen_name, cursor=cursor)
                else:  # user_id
                    response = twitter_api_func(user_id=user_id, cursor=cursor)

            except TwitterHTTPError, e:  # if exception occurs go to sleep
                debug_print(e)
                debug_print("  Rate limit reached. Start:" + str(time.ctime()) + " . Retrying in 15 min ...zZz...")
                sys.stderr.flush()
                logger.error(e)
                time.sleep(15*60 + 10)
                debug_print("  Woke up ... End: " + str(time.ctime()))
                debug_print("  cursor after waking up: "+str(cursor))


            else:  # collect the ids from this response and set the cursor to the next page
                if response is not None:
                    ids += response['ids']
                    cursor = response['next_cursor']

                print >> sys.stderr, '  Fetched: {0} total: {1} ids for: {2}'.format(len(ids),
                                        label, (user_id or screen_name))

                if len(ids) >= limit or response is None:
                    break

    return friends_ids[:friends_limit], followers_ids[:followers_limit]



def twitter_user_timeline(twitter_api, screen_name=None, user_id=None, max_results=2000):
    """
    Harvest all of user's most recent tweets and save into database. Number of retrieved tweets can grow to 3,200
    so a robust API wrapper is added
    :parameter: screen_name - owner of timeline
    :parameter: user_id - id of owner of timeline
    :parameter: max_results
    :returns results - tweets from  user'r timeline
    """
    debug_print('EXEC twitter_user_timeline method : ')
    assert (screen_name != None) != (user_id != None), \
        "Must have screen_name or user_id, but not both"

    kw = { # Keyword args for the TwitterWrapper API call
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
    tweets = tt.make_robust_request(twitter_api.statuses.user_timeline, **kw)

    if tweets is None:  # 401 (Not Authorized) - Need to bail out on loop entry
        tweets = []

    results += tweets
    debug_print('  Fetched %i tweets' % len(tweets))
    page_num = 1

    if max_results and max_results == kw['count']:
        page_num = max_pages # Prevent loop entry

    while page_num < max_pages and len(tweets) > 0 and len(results) < max_results:
        # Necessary for traversing the timeline in TwitterWrapper's v1.1 API:
        # get the next query's max-id parameter to pass in.
        # See https://dev.twitter.com/docs/working-with-timelines.

        kw['max_id'] = min([tweet['id'] for tweet in tweets]) - 1
        #if there are more tweets make a request for them with max id included
        tweets = tt.make_robust_request(twitter_api.statuses.user_timeline, **kw)
        results += tweets
        debug_print('  Fetched %i tweets' % (len(tweets)))
        page_num += 1
    debug_print('  Done fetching tweets')

    indexes = ["hashtags.text"]
    DB.twitter_save_to_mongo(data=tweets, mongo_db="twitter", mongo_db_coll=screen_name, indexes=indexes)

    return results[:max_results]


def twitter_get_user_info(twitter_api , screen_name=None , user_id=None):
    """ Function that retrieves information for a given user
    :parameter twitter_api
    :parameter user_id or screen_name

    :returns user - json object with all information about user"""
    debug_print('EXEC twitter_get_user_info method : ')

    user = None

    if screen_name and not user_id:
        user = twitter_api.users.show(screen_name=screen_name)
    elif user_id and not screen_name:
        user = twitter_api.users.show(user_id=user_id)

    if user:
        return  user


# ANALSYSI FUNCTIONS


def twitter_date_of_last_tweet(owner_screen_name,slug):
    """
     Get the date of the last tweet for a screen_name, from database

    :parameter: screen_name:
    :return: date of last tweet
    """

    result = DB.twitter_load_from_mongo_sorted(mongo_db=DEFAULT_MONGO_DB, mongo_db_coll=slug,criteria={"user.screen_name":owner_screen_name}, limit=1)
    if result:
        last_tweet = result[0]
        return last_tweet["DATE"]
    else:
        return 0


def twitter_date_of_fifth_tweet(owner_screen_name,slug):
    """
    Get the date of the fifth tweet for a given screen_name.
    If less than five tweets are posted then returns the last.

    :parameter: screen_name:
    :return: date of the fifth tweet sorted in DESC order
    """
    result = DB.twitter_load_from_mongo_sorted(mongo_db=DEFAULT_MONGO_DB,mongo_db_coll=slug,criteria={"user.screen_name":owner_screen_name}, limit=5)
    idx = len(result)-1
    if len(result) > 0: #check if there are any posts in database for this screen_name
        fifth_tweet = result[idx]
        return fifth_tweet["DATE"]
    else:  # no tweets saved in database
        return 0

