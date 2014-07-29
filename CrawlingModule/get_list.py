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
import twitter
import logging
logger = logging.getLogger(__name__)
logger = setup_logging(logger)



def get_list_memebers_statuses(twitter_api, max_results=1000,owner_screen_name = "@spartakan", slug="community-councils"):
    debug_print("EXEC get_list_members method :")

    #get last tweet from mongo
    since_id = load_from_mongo(mongo_db="twitter", mongo_db_coll=slug, find_since_id=True)
    if since_id is None:
        since_id = 1

    debug_print("1. Getting since_id from db: "+str(since_id))
    kw = {
        'count': 100,
        'since_id': since_id,
        'include_rts': False
    }
    #get all statuses from list members
    response = twitter_api.lists.statuses(owner_screen_name=owner_screen_name, slug=slug,
                                          **kw)

    #401 (Not Authorized) - Need to bail out on loop entry
    if response is None:
        response = []

    debug_print("2. First response len : "+str(len(response)))
    results = response
    #print json.dumps(response,indent=1)
    page_num = 1
    max_pages = 16

    if max_results == kw['count']:
        page_num = max_pages # Prevent loop entry

    #find all new tweets after the first response
    while page_num < max_pages and len(response) > 0 and len(results) < max_results:
        kw['max_id'] = min([tweet['id'] for tweet in response]) - 1
        response = twitter_api.lists.statuses(owner_screen_name=owner_screen_name, slug=slug, **kw)
        results += response
        debug_print(str(page_num+2)+". All results len : "+str(len(results)) + " |  New response len : "+str(len(response)))
        page_num += 1

    #Saving all results to database
    for tweet in results:
        #print json.dumps(tweet, indent=1)
        save_to_mongo(tweet, "twitter", slug)
    debug_print(str(page_num+2)+". All Results are saved in database")




def get_list_memebers(twitter_api, owner_screen_name="spartakan", slug="community-councils"):
    debug_print("EXEC get_list_members method :")
    members = []
    cursor = -1
    #get all members of the list
    while cursor != 0:
        try:
            response = twitter_api.lists.members(owner_screen_name=owner_screen_name, slug=slug, cursor=cursor)
            debug_print("  next cursor: " + str(response['next_cursor']))
            if response is not None:

                cursor = response['next_cursor']
                members += response['users']
                debug_print("  users (last response): " + str(len(response['users'])))
                debug_print("  total members: " + str(len(members)))
        except TwitterHTTPError, e:
            debug_print(e)
            sys.stderr.flush()
            debug_print("  Rate limit reached . Retrying in 15 min ...zZz...")
            logger.error(e)
            time.sleep(60*15 + 10)
            debug_print("  Woke up ... ")
            debug_print("  cursor after waking up: "+str(cursor))
    return members

