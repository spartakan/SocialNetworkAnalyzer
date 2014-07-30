from functools import partial
from sys import maxint
import sys, os, platform
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from debugging_setup import debug_print
from twitter.api import TwitterHTTPError
import time
from debugging_setup import setup_logging, debug_print
import logging
logger = logging.getLogger(__name__)
logger = setup_logging(logger)


def get_friends_followers(twitter_api, screen_name=None, user_id=None,
                              friends_limit=maxint, followers_limit=maxint):
    debug_print("EXEC get_friends_followers method :")
    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None), \
    "Must have screen_name or user_id, but not both"

    # See https://dev.twitter.com/docs/api/1.1/get/friends/ids and
    # https://dev.twitter.com/docs/api/1.1/get/followers/ids for details
    # on API parameters

    #return only ids of list members
    # get_friends_ids = partial(twitter_api.friends.ids,count=5000)
    # get_followers_ids = partial(twitter_api.followers.ids,count=5000)
    #
    # friends_ids, followers_ids = [], []
    #
    # for twitter_api_func, limit, ids, label in [
    #                 [get_friends_ids, friends_limit, friends_ids, "friends"],
    #                 [get_followers_ids, followers_limit, followers_ids, "followers"]
    #             ]:
    #
    #     if limit == 0: continue
    #
    #     cursor = -1
    #     while cursor != 0:
    #
    #         # Use make_twitter_request via the partially bound callable...
    #         if screen_name:
    #             response = twitter_api_func(screen_name=screen_name, cursor=cursor)
    #         else: # user_id
    #             response = twitter_api_func(user_id=user_id, cursor=cursor)
    #
    #         if response is not None:
    #             ids += response['ids']
    #             cursor = response['next_cursor']
    #
    #         print >> sys.stderr, 'Fetched {0} total {1} ids for {2}'.format(len(ids),
    #                                                 label, (user_id or screen_name))
    #
    #         # XXX: You may want to store data during each iteration to provide an
    #         # an additional layer of protection from exceptional circumstances
    #
    #         if len(ids) >= limit or response is None:
    #             break
    #
    # # Do something useful with the IDs, like store them to disk...
    # return friends_ids[:friends_limit], followers_ids[:followers_limit]

    #get the whole json object for each user

    get_followers = partial(twitter_api.followers.list, count=followers_limit)
    cursor = -1
    followers = []

    while cursor != 0:
        try:
            response = get_followers(screen_name=screen_name, cursor=cursor)
            if response is not None:
                cursor = response['next_cursor']
                followers += response['users']
                debug_print("  users (last response): %d " % (len(response['users'])))
                debug_print("  total followers: %d" % len(followers))
        except TwitterHTTPError, e:
            debug_print(e)
            sys.stderr.flush()
            logger.error(e)
            if e.e.code == 88:
                debug_print("  Rate limit reached. Start: %s . Retrying in 15 min ...zZz..." % (str(time.ctime())))
                time.sleep(60*15 + 10)
                debug_print("  Woke up ... End: %s"  % (str(time.ctime())))
    return followers
