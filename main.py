#!/usr/bin/python
from functools import partial
import sys
from config import *

#Defaults (to move to config file)

import json      # Used for debug only
import xlrd,xlwt # Spreadsheet manip
import networkx as nx

import Twitter.authorization as cta
import Twitter.user as ctu
import Twitter.tweets as tt
import Twitter.list as tl

from DB.twitter import twitter_load_from_mongo_sorted,twitter_save_to_mongo, \
                        save_to_mongo, load_from_mongo, getCollections

from Twitter.Analysis.tweets import get_common_tweet_entities,extract_tweet_entities,print_prettytable, \
                                          get_popular_hashtags, get_users_for_hashtag_list,\
                                          find_popular_tweets,twitter_get_hashtags_from_tweets
from Twitter.Analysis.graph import create_keyplayers_graph,export_graph_to_gml,create_directed_graph_of_list_members_and_followers,create_multi_graph_of_list_memebers_and_followers
from Twitter.user import twitter_date_of_fifth_tweet,twitter_date_of_last_tweet

logger = logging.getLogger(__name__)
logger = setup_logging(logger)


def help():
    print "These are your options: "
    print "follow-list  <user> <list> Set up loop to save tweets from list members on interval"
    print "get-list <user> <list>. Save a list of list members"
    print "get-list-references <user> <list>. Get references to list members"
    print "get-list-tweets <user> <list>. Get statuses of list members"
    print "search <query>. Search & save tweets for a specific query"
    print "ssearch <query>. Search & save tweets from the streaming api"
    print "\nUNTESTED:"
    print "0. Find users who have tweeted a hashtag , for a list of popular hashtags"
    print "1. Get only hashtags from results"
    print "2. Create & export graph of members of twitter list and their followers"
    print "4. Find the trending topics in the world (BUGGY))"
    print "5  Call function for saving tweets from list members on interval( predefined for community-council)"
    print "6. Get info about list members from api (json)"
    print "9. Get all tweets from a user's timeline"
    print "10. Print common entities"
    print "11. Get list members"
    print "12. MULTIGRAPH"
    print "13. find  popular tweets from list of tweets"
    print "14. Get twitter info about a specific user"
    print "15. Get date for last tweet"
    print "16. Get date for fifth tweet"
    print "17. Create excel file with statistcs for members of twitter list"
    print '\nNOTE: Default user=%s list=%s.\nResults are saved to MongoDB=%s'%(DEFAULT_TWITTER_USER,DEFAULT_TWITTER_LIST,DEFAULT_MONGO_DB)

#menu with functions and options for twitter
def main():
    if len(sys.argv) <= 1:
        action = None
        help()
    else:
        action = sys.argv[1]
        debug_print(("Action=%s")%action)
        param1 = None
        param2 = None
        if len(sys.argv) >= 3:
            param1 = sys.argv[2]
            if len(sys.argv) >= 4:
                param2 = sys.argv[3]

        api = cta.twitter_authorize()
        if not(api):
            print "Twitter authorisation fail"
        else:
            debug_print("Successfully authenticated and authorized")

            if False:
                None

            elif action in ['5', 'follow-list']:  # find trending topics on a time interval
                twUser = param1 if param1 else DEFAULT_TWITTER_USER
                twList = param2 if param2 else DEFAULT_TWITTER_LIST
                #making a partial class from twitter_search to later add it as an argument in twitter_call_function_on_interval
                tweets_from_list_members = partial(tl.save_list_members_tweets, api, owner_screen_name=twUser, slug=twList)
                #get and save the trending topics on time intervals
                tt.call_function_on_interval(tweets_from_list_members)

            elif action in ['6', 'get-list']:  # find trending topics on a time interval
                twUser = param1 if param1 else DEFAULT_TWITTER_USER
                twList = param2 if param2 else DEFAULT_TWITTER_LIST
                tl.save_list_members(api,owner_screen_name=twUser, slug=twList)


            elif action == 'get-list-references':
                # Cycle through all list members and for each, find all references
                # TODO: Turn into a function (somewhere) and handle API limits (use call_function_on_interval())
                twUser = param1 if param1 else DEFAULT_TWITTER_USER
                twList = param2 if param2 else DEFAULT_TWITTER_LIST
                members = tl.fetch_list_members(slug=twList)
                for m in members:
                    q = "@%s"%(m["screen_name"])
                    debug_print("Searching tweets for the query:" + q)
                    results = tt.search(api, q, 50, "%s_%s"%(twList,"references"))
                    debug_print("Tweets saved into database %s_%s"%(twList,"references"))
                    # db.getCollection("community-councils_references").find({},{_id:0,"user.screen_name":1,"entities.user_mentions.screen_name":1,"text":1})

            elif action == 'get-list-tweets':  # get statuses of list members
                twUser = param1 if param1 else DEFAULT_TWITTER_USER
                twList = param2 if param2 else DEFAULT_TWITTER_LIST
                tl.save_list_members_tweets(api, owner_screen_name=twUser, slug=twList)

            elif action == 'search':
                #~ Syntax guide: https://dev.twitter.com/docs/using-search )  "
                q = param1

                if q:
                    debug_print("Searching tweets for the query:" + q)
                    #twitter_call_function_on_interval(search_tweets, 'twitter', q)
                    results = tt.search(api, q, 1000)
                    debug_print("Tweets saved into database")

                else:
                    print "Query missing"


            elif action == 'ssearch':
                q = param1
                if q:
                    debug_print("Searching and saving tweets from the streaming api for query: " +q+ "...")
                    tt.stream_api(api, q)
                else:
                    print "Query missing"



            # Untested and flaky features below
            elif action == '0':  # find users who have tweeted a hashtag , for a list of popular hashtags
                hashtags_dict = get_popular_hashtags(slug="community-councils")
                hashtags = hashtags_dict.keys() #.sort()
                debug_print(hashtags_dict)
                for hashtag in hashtags:
                    print hashtag
                #dict = get_users_for_hashtag_list(hashtags_dict.keys())


            elif action == '1': #  get only hashtags from results
                results = load_from_mongo(mongo_db="twitter", mongo_db_coll="community-councils")
                hashtags = twitter_get_hashtags_from_tweets(results)
                print "num of hashtags: ", len(hashtags)
                for hashtag in hashtags:
                    print "#", hashtag


            elif action == '2': # create & export graph of members of twitter list and their followers
                #create directed graph of members of a list and their followers
                #save list of followers for each member into a separate collection named after the slug ending with  _member
                slug="community-councils"
                graph = create_directed_graph_of_list_members_and_followers(api, slug)
                export_graph_to_gml(graph,path_to_graph_file)


            elif action == '4':  # Get trending topics
                print "INFO: Getting World Trends ..."
                WORLD_WOE_ID = 1  # for searching trends
                world_trends = tt.trends(api, WORLD_WOE_ID)
                #for checking the structure of uncomment : #print json.dumps(world_trends[0]['trends'], indent=1)
                if world_trends:
                    world_trends = world_trends[0]['trends']
                    for w in world_trends:
                        print "trend: ", w['name']


            elif action == '9':  # Get all tweets from a user's timeline
                    screen_name = param1 if param1 else DEFAULT_TWITTER_USER
                    tweets = ctu.twitter_user_timeline(api, screen_name=screen_name)


            elif action == '10':
                    results = load_from_mongo("twitter", "#indyref")
                    common_entities = get_common_tweet_entities(results)
                    print_prettytable(common_entities)

            elif action == '11':  # get list members
                twUser = param1 if param1 else DEFAULT_TWITTER_USER
                twList = param2 if param2 else DEFAULT_TWITTER_LIST
                tl.save_list_members(api,owner_screen_name=twUser, slug=twList)

            elif action == '12':
                print "MULTIGRAPH"
                twList = param1 if param1 else DEFAULT_TWITTER_LIST
                mdG = create_multi_graph_of_list_memebers_and_followers(api,twList)
                name_of_file = "twitter_multigraph.gml"
                export_graph_to_gml(mdG, path_to_graph_file + name_of_file)


            elif action == '13':  # find popular tweets from list of tweets
                twList = param1 if param1 else DEFAULT_TWITTER_LIST
                statuses = load_from_mongo(DEFAULT_MONGO_COLLECTION, twList)
                find_popular_tweets(statuses=statuses)

            elif action == '14':  # get info for user
                screen_name = param1 if param1 else DEFAULT_TWITTER_USER
                user = ctu.twitter_get_user_info(api, screen_name)
                debug_print(json.dumps(user, indent=1))

            elif action == '15':
                screen_name = param1 if param1 else DEFAULT_TWITTER_USER
                print twitter_date_of_last_tweet(screen_name)

            elif action == '16':
                screen_name = param1 if param1 else DEFAULT_TWITTER_USER
                print twitter_date_of_fifth_tweet(screen_name)


            elif action == '17':
                #TODO Rewrite as a method elsewhere
                #print(facebook_path_to_EXPORT_FILE)

                # Load data
                members = load_from_mongo(mongo_db="twitter", mongo_db_coll="community-councils_members")  # collection where all
                                                                                               # the data for each page is stored
                pages_data = facebook_sort_pages(members, "DESC")

                # Prepare to output
                workbook = xlwt.Workbook(encoding="utf-8")  # XLWT - ONLY EXPORTS .XLS files
                sheet = workbook.add_sheet("sheet1")
                sheet.write(0, 0, 'ID ')
                sheet.write(0, 1, 'CC screen_name')
                sheet.write(0, 2, 'Count Followers')
                sheet.write(0, 3, 'Count Friends')
                sheet.write(0, 4, 'Count Posts TOTAL')
                sheet.write(0, 5, 'Date Most recent post')
                sheet.write(0, 6, 'Date 5th Most recent post')

                i = 1  # index for rows in sheet
                for member in members:
                    sheet.write(i, 0, member['id'])
                    sheet.write(i, 1, member['screen_name'])
                    sheet.write(i, 2, member['followers_count'])
                    sheet.write(i, 3, member['friends_count'])

                    most_recent_post = twitter_date_of_last_tweet(member['screen_name'],"community-councils")
                    fifth_most_recent_post = twitter_date_of_fifth_tweet(member['screen_name'],"community-councils")
                    sheet.write(i, 5, most_recent_post)
                    sheet.write(i, 6, fifth_most_recent_post)
                    #total
                    sheet.write(i, 4, member["statuses_count"])

                    i += 1
                workbook.save(twitter_path_to_EXPORT_FILE)
            else:
                help()


if __name__ == '__main__':
    main()


