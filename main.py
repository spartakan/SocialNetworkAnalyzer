from functools import partial

import networkx as nx
import json
from config import *
from CrawlingModule.Twitter.authorization import twitter_authorize
from CrawlingModule.Twitter.user import twitter_get_followers, twitter_user_timeline
from CrawlingModule.Twitter.tweets import twitter_search, twitter_call_function_on_interval, twitter_stream_api,twitter_trends
from CrawlingModule.Twitter.list import twitter_get_list_members, twitter_get_list_members_tweets
from CrawlingModule.Facebook.authorization import facebook_authorize
from CrawlingModule.Facebook.pages import facebook_get_page_data, facebook_get_page_posts,facebook_sort_pages, \
                                        facebook_read_pages_from_excel,facebook_print_page_data

from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from DatabaseModule.FacebookWrapper.database_manipulation import facebook_save_to_mongo

from AnalysisModule.Twitter.tweets import get_common_tweet_entities,extract_tweet_entities,print_prettytable, \
    get_popular_hashtags, get_users_for_hashtag_list,\
                                    find_popular_tweets
from AnalysisModule.Twitter.graph import create_keyplayers_graph,export_graph_to_gml
from AnalysisModule.Facebook.pages import facebook_get_likes_count,facebook_get_talkingabout_count, facebook_get_posts

logger = logging.getLogger(__name__)
logger = setup_logging(logger)









def facebook_menu():
    access_token = facebook_authorize()
    action = None
    while not action:
            print "Type the number of the action you want to be executed: "
            print "0. Save posts for each facebook page read from excel file"
            print "1. Print sorted pages by number of likes and talking about parameter "
            print "2. Save data for each page from list "
            print "3. Get likes per page"
            print "4. Get talking about count per page"
            print "5. Get facebook posts sorted"
            print "6. Save posts for one page"

            action = raw_input('Enter the number of the action: ').strip()
    if action == '0' or action == '1':
        pages = facebook_read_pages_from_excel(access_token)  # get pages and basic data for pages
        if action == '0':
            for i in range(0, len(pages)):
                results = facebook_get_page_posts(access_token, pages[i]["id"]) #send id of page and access token to get posts
                facebook_save_to_mongo(mongo_db="facebook", mongo_db_coll=pages[i]['name'], data=results)

        if action == '1':
            sorted_pages = facebook_sort_pages(pages, "DESC")
            facebook_print_page_data(sorted_pages)
    elif action == '2':
        pages = facebook_read_pages_from_excel(access_token)
        print len(pages)
        for page in pages:
            data = facebook_get_page_data(access_token, page)
            if data:
                facebook_save_to_mongo(mongo_db="facebook", mongo_db_coll="pages_info", data=data)

    elif action == '3':
        page = "Connel Community Council"  #sample page
        print page, facebook_get_likes_count(page)

    elif action == '4':
        page = "Connel Community Council" #sample page
        print page, facebook_get_talkingabout_count(page)
    elif action == '5':
        posts = facebook_get_posts(from_user="Connel Community Council", page_name="Connel Community Council")
        for post in posts:
            print post
            print "\n  \n _________________________________________________________________________ \n"
            #break
    elif action == '6':
        page = "187281984718895"  # sample id
        data = facebook_get_page_posts(access_token, page, limit=500)
        debug_print("posts from api  :%i" % len(data))
        for post in data:
            facebook_save_to_mongo(mongo_db="facebook", mongo_db_coll="Connel Community Council", data=post)









def twitter_menu():
    api = twitter_authorize()
    if api:
        debug_print("Successfully authenticated and authorized")
        action = None
        while not action:
            print "Type the number of the action you want to be executed: "
            print "0. Find users who have tweeted a hashtag , for a list of popular hashtags"
            print "1. Get only hashtags from results"
            print "2. Create & export graph of members of twitter list and their followers"
            print "3. Get statuses of list members"
            print "4. Find the trending topics in the world"
            print "5. Search & save trending topics on 15 seconds"
            print "6. Get list members"
            print "7. Search & save tweets for a specific query"
            print "8. Search & save tweets from the streaming api"

            print "9. Get all tweets from a user's timeline"
            print "10. Print common entities"
            print "11. Get list members"
            print "12. create a directed graph of members of a list and their followers"
            print "13. find  popular tweets from list of tweets"
            action = raw_input('Enter the number of the action: ').strip()

        WORLD_WOE_ID = 1  # for searching trends

        if action == '0':  # find users who have tweeted a hashtag , for a list of popular hashtags
            hashtags_dict = get_popular_hashtags()
            hashtags = hashtags_dict.keys()
            for hashtag in hashtags:
                print hashtag
            dict = get_users_for_hashtag_list(hashtags_dict.keys())

        elif action == '1': #  get only hashtags from results
            results = load_from_mongo(mongo_db="twitter", mongo_db_coll="community-councils")
            screen_names, hashtags, urls, media, symbols = extract_tweet_entities(results)
            #remove duplicates
            hashtags = set(hashtags)
            print "num of hashtags: ", len(hashtags)
            for hashtag in hashtags:
                print "#", hashtag

        elif action == '2': # create & export graph of members of twitter list and their followers
            criteria = {"in_reply_to_user_id": {"$ne": None}, "$where": "this.user.id != this.in_reply_to_user_id"}
            projection = {"id": 1, "user.screen_name": 1, "in_reply_to_screen_name": 1, "in_reply_to_user_id": 1, "text": 1}
            results = load_from_mongo(mongo_db="twitter", mongo_db_coll="community-councils",
                                      criteria=criteria, projection=projection)

            debug_print("  num of edges/results: %d" % len(results))
            G = nx.DiGraph()
            members = twitter_get_list_members(api)
            debug_print("  num of members: %d" % len(members))
            for member in members:
                G.add_node(member['id'], screen_name=member['screen_name'], location=member['location'],
                   followers_count=member['followers_count'], statuses_count=member['followers_count'],
                   friends_count=member['friends_count'], created_at=member['created_at'])
            i = 0
            for result in results:

                if G.has_node(result['id']) and G.has_node(result['in_reply_to_user_id']):
                    debug_print("%d) user: %s \n          in reply to: %s \n          text: %s" % (i,result['user']['screen_name'],result['in_reply_to_screen_name'],result['text']))
                    i += 1
                    G.add_edge(result['id'], result['in_reply_to_user_id'])
            export_graph_to_gml(G, path_to_graph_file)

        elif action == '3':  # get statuses of list members
            twitter_get_list_members_tweets(api, owner_screen_name="spartakan", slug="community-councils")

        elif action == '4':  # Get trending topics
            print "INFO: Getting World Trends ..."
            world_trends = twitter_trends(api, WORLD_WOE_ID)
            #for checking the structure of uncomment : #print json.dumps(world_trends[0]['trends'], indent=1)
            if world_trends:
                world_trends = world_trends[0]['trends']
                for w in world_trends:
                    print "trend: ", w['name']

        elif action == '5':  # find trending topics on a time interval
            #making a partial class from twitter_search to later add it as an argument in twitter_call_function_on_interval
            tweets_from_list_members = partial(twitter_get_list_members_tweets, api)
            #get and save the trending topics on time intervals
            twitter_call_function_on_interval(tweets_from_list_members)

        elif action == '6':  # get members of a list
            twitter_get_list_members(api)

        elif action == '7' or action == '8':
            q = None
            print "Read How to build a query first ! ( https://dev.twitter.com/docs/using-search )  "
            q = raw_input('Enter a query: ').strip()
            while not q:
                q = raw_input('Enter a query:').strip()
            if action == '7':  # Fetch tweets from the search/rest api
                debug_print("Searching tweets for the query:" + q)
                #twitter_call_function_on_interval(search_tweets, 'twitter', q)
                results = twitter_search(api, q, 1000)
                debug_print("Tweets saved into database")

            if action == '8':  # Fetch tweets from streaming api
                debug_print("Searching and saving tweets from the streaming api for query: " +q+ "...")
                twitter_stream_api(api, q)

        elif action == '9':  # Get all tweets from a user's timeline
                screen_name = raw_input('Enter the screen name: ').strip()
                while not screen_name:
                    screen_name = raw_input('Enter a query:').strip()
                debug_print("Getting tweets from user: " + screen_name + " ... ")
                tweets = twitter_user_timeline(api, screen_name="SocialWebMining", max_results=200)
                save_to_mongo(tweets, "twitter", screen_name, indexes="hashtags.text")

        elif action == '10':
                results = load_from_mongo("twitter", "#indyref")
                common_entities = get_common_tweet_entities(results)
                print_prettytable(common_entities)

        elif action == '11':  # get list members
            twitter_get_list_members(api)

        elif action == '12':
            #create directed graph of members of a list and their followers
            #save list of followers for each member into a separate collection named after the slug ending with  _member
                graph = nx.DiGraph()
                slug = "FollowLater-Macedonia"
                db_coll_name = "%s_%s" % (slug, "members")
                owner = "BalkanBabes"
                members = twitter_get_list_members(api, slug=slug, owner_screen_name=owner)

                #add all the connections between the members and their followers
                for member in members[:15]:
                    followers = twitter_get_followers(api, screen_name=member['screen_name'], followers_limit=100)
                    #save each member to database
                    save_to_mongo(data=member, mongo_db="twitter", mongo_db_coll=db_coll_name)

                    #save each follower of each member to database
                    for follower in followers:
                        save_to_mongo(data=follower, mongo_db="twitter", mongo_db_coll=db_coll_name)

                    graph = create_keyplayers_graph(graph=graph, user=member, followers=followers)
                export_graph_to_gml(graph,path_to_graph_file)

        elif action == '13':  # find popular tweets from list of tweets
            statuses = load_from_mongo("twitter", "community-councils")
            find_popular_tweets(statuses=statuses)

        else:
            print "WRONG ACTION!!!"
    else:
        print "You are not authorized!!!"













def main():

    action = None
    while not action:
        action = raw_input('For Twitter type in T | Facebook type in F : ').strip()
        if action == 'T':
            twitter_menu()
        elif action == 'F':
            facebook_menu()
        else:
            print "WRONG ACTION!!!"

if __name__ == '__main__':
    main()




