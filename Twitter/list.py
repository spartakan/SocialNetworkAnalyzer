import json, time

from twitter.api import TwitterHTTPError

# SNA imports
from config import *
from DB.twitter import twitter_save_to_mongo, \
                        load_from_mongo,save_to_mongo, twitter_load_from_mongo_sorted
#~ from Common.DB import load_from_mongo,save_to_mongo
import Twitter.tweets as tt

from debugging_setup import setup_logging, debug_print
logger = logging.getLogger(__name__)
logger = setup_logging(logger)


def save_list_members_tweets(twitter_api, max_results=1000, owner_screen_name="", slug=""):
    """Gets all tweets from twitter api posted by list members and stores them into database
    :parameter: twitter_api
    :parameter: max_results
    :parameter: owner_screen_name - name of the creator of the list
    :parameter: slug - the name of the list
    """
    debug_print("EXEC twitter_get_list_members method :")

    #get id of last tweet from mongo
    since_id = load_from_mongo(mongo_db=DEFAULT_MONGO_DB, mongo_db_coll=slug, find_since_id=True)
    if since_id is None:
        since_id = 1

    debug_print("  Getting since_id from db: "+str(since_id))
    kw = {
        'count': 100,
        'since_id': since_id,
        'include_rts': False
    }
    #get all statuses from list members
    response = twitter_api.lists.statuses(owner_screen_name=owner_screen_name, slug=slug,**kw)
    #401 (Not Authorized) - Need to bail out on loop entry
    if response is None:
        response = []

    debug_print("  First response len : "+str(len(response)))
    results = response
    page_num = 1
    max_pages = 16

    if max_results == kw['count']:
        page_num = max_pages # Prevent loop entry

    #find all new tweets after the first response
    while page_num < max_pages and len(response) > 0 and len(results) < max_results:
        kw['max_id'] = min([tweet['id'] for tweet in response]) - 1
        response = twitter_api.lists.statuses(owner_screen_name=owner_screen_name, slug=slug, **kw)
        results += response
        #debug_print("  All results len : "+str(len(results)) + " |  New response len : "+str(len(response)))
        page_num += 1

    #Saving all results to database

    twitter_save_to_mongo(results, DEFAULT_MONGO_DB, slug)
    #debug_print(" All Results are saved in database")


def save_list_members(twitter_api, owner_screen_name="", slug=""):
    """ Gets information about all the members in a list from twitter api and stores them into database
    :parameter: twitter_api
    :parameter: owner_screen_name - name of the person who created the list
    :parameter: slug - name of the list
    """
    debug_print("EXEC twitter_get_list_members method :")
    members = []
    cursor = -1
    #get all members from the list (returns full json objects)
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
            debug_print("  Rate limit reached. Start:" + str(time.ctime()) + " . Retrying in 15 min ...zZz...")
            logger.error(e)
            time.sleep(15*60 + 10)
            debug_print("  Woke up ... End: " + str(time.ctime()))
            debug_print("  cursor after waking up: "+str(cursor))
    db_coll_name = "%s_%s" % (slug, "members") #create database name for members  format = > slug_members
    save_to_mongo(members, mongo_db=DEFAULT_MONGO_DB, mongo_db_coll=db_coll_name)
    return members


def save_list_references(twitter_api, owner_screen_name="", owner_list=""):
    """ Cycle through all list members and for each, find all references PAC 20150408
    """
    members = fetch_list_members(slug=owner_list)
    collection_name = "%s_%s"%(owner_list,"references")
    for m in members:
        member_name = "@%s"%(m["screen_name"])
        # Find ID of last tweet referring to this member
        # db.getCollection("community-councils_references").find({"entities.user_mentions.screen_name":"gilmertoninchcc"}, {_id:0,id:1,"user.screen_name":1,"entities.user_mentions.screen_name":1,"text":1})
        #load_from_mongo()
        since_id = None
        #since_id = load_from_mongo(mongo_db=DEFAULT_MONGO_DB, mongo_db_coll=owner_list, find_since_id=True)
        # TODO Add query to search for member_name

        # Ask twitter for tweets since then & save them - or bail out if rate limit reached
        debug_print("since_id %s:"%since_id)
        debug_print("finding tweets to member %s for %s:"%(member_name,collection_name))
        results = tt.search(twitter_api, member_name, 50, collection_name) # NB tt.search also saves data...
        debug_print("Tweets saved into collection %s"%collection_name)
        # db.getCollection("community-councils_references").find({},{_id:0,"user.screen_name":1,"entities.user_mentions.screen_name":1,"text":1})



def fetch_list_members(slug=""):
    """Return a list of list members
    TODO: This should really be an iterator"""
    mongo_db_coll = "%s_%s" % (slug, "members") #create database name for members  format = > slug_members
    #~ members = twitter_load_from_mongo_sorted(mongo_db=DEFAULT_MONGO_DB,mongo_db_coll=slug,criteria={"screen_name":1}, limit=5)
    members = twitter_load_from_mongo_sorted(mongo_db=DEFAULT_MONGO_DB,mongo_db_coll=mongo_db_coll, criteria=None, limit=None)
    for m in members:
        print m["screen_name"]
    return members

