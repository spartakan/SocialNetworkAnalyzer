from functools import partial
import sys, os, platform, time, logging
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from twitter.api import TwitterHTTPError
from debugging_setup import setup_logging, debug_print
from sys import maxint

#create a logger for this module , set it up, and use it to write errors to file
logger = logging.getLogger(__name__)
logger = setup_logging(logger)


def get_followers(twitter_api, screen_name=None, followers_limit=None):
    """ Retrieve a list of followers(full information represented as a json file) for a specific user.
        For more information on how the file is structured check https://dev.twitter.com/docs/api/1.1/get/followers/list
    :parameter twitter_api
    :parameter screen_name - The screen name of the user for whom to return results for
    :parameter followers_limit - The maximum number of users to return
    :returns followers - list of followers, each represented as a json object
    """
    debug_print("EXEC get_followers method :")
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
                response = twitter_api.followers.list(count=5000, screen_name=screen_name, cursor=cursor)
                if response is not None:
                    cursor = response['next_cursor']
                    followers += response['users']
                    debug_print("  users (last response): %d " % (len(response['users'])))
                    debug_print("  total followers: %d" % len(followers))
            except TwitterHTTPError, e:
                debug_print(e)
                sys.stderr.flush()
                logger.error(e)
                if e.e.code == 88:   # rate limit is reached
                    debug_print("  Rate limit reached. Start: %s . Retrying in 15 min ...zZz..." % (str(time.ctime())))
                    time.sleep(60*15 + 10)
                    debug_print("  Woke up ... End: %s"  % (str(time.ctime())))
    return followers


def get_friends_followers_ids(twitter_api, screen_name=None, user_id=None,
                              friends_limit=maxint, followers_limit=maxint):
    """ Retrieves all the ids of friends and followers for a specific user.
    :parameter twitter_api
    :parameter screen_name - The screen name of the user for whom to return results for.
    :parameter user_id - The ID of the user for whom to return results for.
    :parameter friends_limit
    :parameter followers_limit
    :returns friends_ids, followers_ids - lists of friends ids and followers ids
    """
    debug_print("EXEC get_friends_followers_ids method :")
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

            # Use make_twitter_request via the partially bound callable...
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