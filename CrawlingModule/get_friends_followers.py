from functools import partial
from sys import maxint
import sys

def get_friends_followers_ids(twitter_api, screen_name=None, user_id=None,
                              friends_limit=maxint, followers_limit=maxint):

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

    followers = partial(twitter_api.followers, count=100)
    return followers
