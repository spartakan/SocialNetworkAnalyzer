
from config import *
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
logger = logging.getLogger(__name__)
logger = setup_logging(logger)



def get_tweets_form_list_members(twitter_api, max_results=1000, slug="FollowLater-Macedonia", owner_screen_name="@BalkanBabes"):
    debug_print("EXEC get_tweets_form_list_members method :")

    #get all the statuses for a specific list and its owner without retweets
    #response = twitter_api.lists.statuses(owner_screen_name = "@spartakan", slug="community-councils",
                                            # count=100,include_rts=False,*kw)

    #get last tweet from mongo
    since_id = load_from_mongo(mongo_db="twitter", mongo_db_coll=slug, find_since_id=True)
    if since_id is None:
        since_id = 1

    debug_print("  Getting since_id from db: "+str(since_id))
    kw = {
        'count': 100,
        'since_id': since_id,
        'include_rts': False,
        'include_entities': True
    }
    response = twitter_api.lists.statuses(owner_screen_name=owner_screen_name, slug=slug,
                                          **kw)

    #401 (Not Authorized) - Need to bail out on loop entry
    if response is None:
        response = []

    debug_print("  First response len : "+str(len(response)))
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
        debug_print("  "+str(page_num)+". All results len : "+str(len(results)) + " |  New response len : "+str(len(response)))
        page_num += 1

    #Saving all results to database
    for tweet in results:
        #print json.dumps(tweet, indent=1)
        save_to_mongo(tweet, "twitter", slug)
    debug_print("  All Results are saved in database")

def get_list_members(twitter_api, owner_screen_name="@spartakan", slug="community-councils"):
    debug_print("EXEC get_list_members method :")
    response = twitter_api.lists.members(owner_screen_name = owner_screen_name, slug=slug)
    #print(json.dumps(members, indent=1))
    next_cursor = response['next_cursor']
    members = response['users']
    while next_cursor:
            debug_print("  num of users: " + str(len(members)))
            response = twitter_api.lists.members(owner_screen_name="@spartakan", slug="community-councils", cursor=next_cursor)
            next_cursor = response['next_cursor']
            members += response['users']

    debug_print("  Total num of users: " + str(len(members)))
    #for u in members:
        #print json.dumps(u,indent =1 )
    return members
