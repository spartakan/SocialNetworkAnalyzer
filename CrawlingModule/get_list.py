import logging,datetime,json,time,sys,twitter
import urllib2, platform, os
from urllib2 import URLError
from httplib import BadStatusLine
from functools import partial
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from debugging_setup import setup_logging, debug_print
from socket import error as SocketError
from twitter.api import TwitterHTTPError
logger = setup_logging()
import twitter



def get_list_memebers(twitter_api,max_results=1000, **kw):
    debug_print("Executing get list members ...")
    #result = twitter_api.lists.list(screen_name = "@spartakan")
    #for r in result:
        #print r['slug']
    # members = twitter_api.lists.members(owner_screen_name = "@spartakan", slug="community-councils")
    #
    # next_cursor = members['next_cursor']
    # users = members['users']
    # while next_cursor:
    #         print "--len: ", len(users)
    #         members = twitter_api.lists.members(owner_screen_name="@spartakan", slug="community-councils", cursor=next_cursor)
    #         next_cursor = members['next_cursor']
    #         users += members['users']
    #
    # print "-total len: ", len(users)
    # print "------------------"
    # for u in users:
    #     print u['screen_name']

    #get all the statuses for a specific list and its owner without retweets
  #  response = twitter_api.lists.statuses(owner_screen_name = "@spartakan", slug="community-councils", count=100,include_rts=False,*kw)
    response = twitter_api.lists.statuses(owner_screen_name = "@BalkanBabes", slug="FollowLater-Macedonia",count =100, include_rts=False, **kw)

    #next_cursor = response['next_cursor']
    print "statuses len : ", len(response)
    results = response
    #print json.dumps(response,indent=1)
    page_num = 1
    max_pages = 16
    if results == max_results:
        page_num = max_pages # Prevent loop entry
    while page_num < max_pages and len(response) > 0 and len(results) < max_results:
        kw['kw'] = min([tweet['id'] for tweet in response]) - 1
        response = twitter_api.lists.statuses(owner_screen_name = "@BalkanBabes", slug="FollowLater-Macedonia", include_rts=False, **kw)
       # response = twitter_api.lists.statuses(owner_screen_name = "@spartakan", slug="community-councils", include_rts=False, **kw)
        results +=response
        print "len rez: ",len(results),"len resp: ",len(response)
