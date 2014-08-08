from functools import partial

import networkx as nx

from config import *
from CrawlingModule.Twitter.authorization import authorize
from CrawlingModule.Twitter.search_tweets import twitter_search, harvest_user_timeline, save_time_series_data, get_and_save_tweets_form_stream_api,twitter_trends
from CrawlingModule.Twitter.twitter_lists_manipulation import get_tweets_form_list_members
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from AnalysisModule.tweets_analysis import get_common_tweet_entities,extract_tweet_entities,print_prettytable, get_popular_tweet_entities_list,get_popular_hashtags,get_users_for_hashtag_list
from AnalysisModule.graph import create_keyplayers_graph,export_graph_to_gml
from CrawlingModule.Twitter.list import get_list_members, get_list_members_statuses


def main():
    api = authorize()
    logger = logging.getLogger(__name__)
    logger = setup_logging(logger)


    if api:
        debug_print("Successfully authenticated and authorized")
        action = None
        while not action:
            print "-3.Find most popular hashtags in a cllection of tweets"
            print "-2.Find all unique hashtags in a cllection of tweets"
            print "Type the number of the action you want to be executed: "
            print "-1. To export data and see who is talking from the members of the list"
            print "0. Save statuses from list members to database"
            print "1. Find the trending topics in the world"
            print "2. Search & save trending topics on 15 seconds"
            print "3. Get list members"
            print "4. Search & save tweets for a specific query"
            print "5. Search & save tweets from the streaming api"
            print "7. Get tweets for specific user account"
            print "8. Analyze entities"
            print "9. Print analysis with pretty table"
            print "10. Print list members"
            print "11. find  followers of list members"
            print "12. find  popular tweets from list members"
            action = raw_input('Enter the number of the action: ').strip()
        WORLD_WOE_ID = 1

        if action == '-3':
            hashtags_dict = get_popular_hashtags()
            hashtags = hashtags_dict.keys()
            for hashtag in hashtags:
                print hashtag
            dict = get_users_for_hashtag_list(hashtags_dict.keys())



        elif action == '-2':
            results = load_from_mongo(mongo_db="twitter", mongo_db_coll="community-councils")
            screen_names, hashtags, urls, media, symbols = extract_tweet_entities(results)
            #remove duplicates
            hashtags = set(hashtags)
            print "num of hashtags: ",len(hashtags)
            for hashtag in hashtags:
                print "#", hashtag

        elif action == '-1':

            criteria = {"in_reply_to_user_id": {"$ne": None}, "$where": "this.user.id != this.in_reply_to_user_id"}
            projection = {"id": 1, "user.screen_name": 1, "in_reply_to_screen_name": 1, "in_reply_to_user_id": 1, "text": 1}
            results = load_from_mongo(mongo_db="twitter", mongo_db_coll="community-councils",
                                      criteria=criteria, projection=projection)

            debug_print("  num of edges/results: %d" % len(results))
            G = nx.DiGraph()
            members = get_list_members(api)
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
            export_graph_to_gml(G, "c:/data/graph_followers_FollowLater-Macedonia.gml")

        elif action == '0':

            get_list_members_statuses(api, owner_screen_name="spartakan", slug="community-councils")

        elif action == '1':
            #print trending topics
            print "INFO: Getting World Trends ..."

            world_trends = twitter_trends(api, WORLD_WOE_ID)
            #for checking the structure of uncomment : #print json.dumps(world_trends[0]['trends'], indent=1)
            if world_trends:
                world_trends = world_trends[0]['trends']
                for w in world_trends:
                    print "trend: ", w['name']

        elif action == '2':
            #making a partial class from twitter_search to later add it as an argument in save_time_series_data
            trending_topics = partial(twitter_trends, api, WORLD_WOE_ID)
            #get and save the trending topics
            save_time_series_data(trending_topics, 'twitter', '#trends')
        elif action == '3':
            get_tweets_form_list_members(api)
        elif action == '4' or action == '5':
            q = None
            print "Read How to build a query first ! ( https://dev.twitter.com/docs/using-search )  "
            q = raw_input('Enter a query: ').strip()
            while not q:
                q = raw_input('Enter a query:').strip()
            if action == '4':
                debug_print("Searching tweets for the query:" + q)
                #save_time_series_data(search_tweets, 'twitter', q)
                results = twitter_search(api, q, 1000)
                debug_print("Tweets saved into database")

            if action == '5':
                debug_print("Searching and saving tweets from the streaming api for query: " +q+ "...")
                get_and_save_tweets_form_stream_api(api, q)

        elif action == '7':
                screen_name = raw_input('Enter the screen name: ').strip()
                while not screen_name:
                    screen_name = raw_input('Enter a query:').strip()
                debug_print("Getting tweets from user: "+ screen_name+ " ... ")
                tweets = harvest_user_timeline(api, screen_name="SocialWebMining", max_results=200)
                save_to_mongo(tweets, "twitter", screen_name, indexes="hashtags.text")

        elif action == '8':
                results = load_from_mongo("twitter", "#indyref")
                get_common_tweet_entities(results)

        elif action == '9':
                results = load_from_mongo("twitter", "#indyref")
                common_entities = get_common_tweet_entities(results)
                print_prettytable(common_entities)
        elif action == '10':
            get_list_members(api)
        elif action == '11':
                #create directed graph
                graph = nx.DiGraph()
                slug = "FollowLater-Macedonia"
                db_coll_name = "%s_%s" % (slug, "members")
                owner = "BalkanBabes"
                members = get_list_members(api, slug=slug,owner_screen_name=owner)

                #add all the connections between the members and their followers
                for member in members[:15]:
                    followers = get_friends_followers(api, screen_name=member['screen_name'],
                                                                        friends_limit=10,
                                                                        followers_limit=100)
                    #save each member to database
                    save_to_mongo(data=member, mongo_db="twitter", mongo_db_coll=db_coll_name)

                    #save each follower to database
                    for follower in followers:
                        save_to_mongo(data=follower, mongo_db="twitter", mongo_db_coll=db_coll_name)

                    graph = create_keyplayers_graph(graph=graph, user=member, followers=followers)
                export_graph_to_gml(graph)
        elif action == '12':
            statuses = load_from_mongo("twitter", "community-councils")
            find_popular_tweets(twitter_api=api, statuses=statuses)

        else:
            print "WRONG ACTION!!!"
    else:
        print "You are not authorized!!!"
if __name__ == '__main__':
    main()




