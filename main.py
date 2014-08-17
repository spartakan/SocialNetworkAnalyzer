from functools import partial

import networkx as nx
import json,xlrd,xlwt

from config import *
from CrawlingModule.Twitter.authorization import twitter_authorize
from CrawlingModule.Twitter.user import twitter_get_followers, twitter_user_timeline,twitter_get_user_info
from CrawlingModule.Twitter.tweets import twitter_search, twitter_call_function_on_interval, twitter_stream_api,twitter_trends
from CrawlingModule.Twitter.list import twitter_get_list_members, twitter_get_list_members_tweets
from CrawlingModule.Facebook.authorization import facebook_authorize
from CrawlingModule.Facebook.pages import facebook_get_page_data, facebook_get_page_posts, \
                                        facebook_read_pages_from_excel,facebook_print_page_data, facebook_print_page_insights

from DatabaseModule.TwitterWrapper.database_manipulation import twitter_load_from_mongo_sorted,twitter_save_to_mongo
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from DatabaseModule.FacebookWrapper.database_manipulation import facebook_save_to_mongo

from AnalysisModule.Twitter.tweets import get_common_tweet_entities,extract_tweet_entities,print_prettytable, \
                                          get_popular_hashtags, get_users_for_hashtag_list,\
                                          find_popular_tweets,twitter_get_hashtags_from_tweets
from AnalysisModule.Twitter.graph import create_keyplayers_graph,export_graph_to_gml,create_directed_graph_of_list_members_and_followers,create_multi_graph_of_list_memebers_and_followers
from AnalysisModule.Twitter.user import twitter_date_of_fifth_tweet,twitter_date_of_last_tweet
from AnalysisModule.Facebook.pages import facebook_get_likes_count,facebook_get_talkingabout_count, \
                                          facebook_get_posts_from_database, facebook_get_posts_for_month,facebook_sort_pages

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
            print "7. Get date from most recent post of a page"
            print "8. Get number of stories for page"
            print "9. Print Facebook insights for a page"
            print "10.Get number of posts for July "

            action = raw_input('Enter the number of the action: ').strip()

    if action == '0' or action == '1' :
        pages = facebook_read_pages_from_excel(access_token)  # get pages and basic data for pages
        if action == '0':
            for page in pages:
                page_data = facebook_get_page_data(access_token, page)
                if page_data:
                    results = facebook_get_page_posts(access_token, page_data["id"]) #send id of page and access token to get posts
                    facebook_save_to_mongo(mongo_db="facebook", mongo_db_coll=page_data['name'], data=results)

        if action == '1':
            sorted_pages = facebook_sort_pages(pages, "DESC")
            facebook_print_page_data(sorted_pages)

        # if action == '10':
        #     for page in pages:
        #         page_data = facebook_get_page_data(access_token, page)
        #         if page_data:
        #             results = facebook_get_page_posts(access_token, page_data["id"]) #send id of page and access token to get posts
        #             facebook_save_to_mongo(mongo_db="facebook", mongo_db_coll=page_data['name'], data=results)

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
        posts = facebook_get_posts_from_database(from_user="Connel Community Council", page_name="Connel Community Council")
        for post in posts:
            print post
            print "\n  \n _________________________________________________________________________ \n"
            #break

    elif action == '6':
        page = "187281984718895"  # sample id
        data = facebook_get_page_posts(access_token, page, limit=500)
        debug_print("posts from api  :%i" % len(data))
        facebook_save_to_mongo(mongo_db="facebook", mongo_db_coll="Connel Community Council", data=data)

    elif action == '7':
        page = "187281984718895"  # sample id
        result = facebook_get_posts_from_database(from_user="Connel Community Council", page_name="Connel Community Council", limit=1)
        print result[0]['created_time']

    elif action == '8':
        #print(facebook_path_to_EXPORT_FILE)
        workbook = xlwt.Workbook(encoding="utf-8")  # XLWT - ONLY EXPORTS .XLS files
        sheet = workbook.add_sheet("sheet1")

        sheet.write(0, 0, 'CC Name')
        sheet.write(0, 1, 'Count Likes')
        sheet.write(0, 2, 'Count Talking about')
        sheet.write(0, 3, 'Count Posts for July')
        sheet.write(0, 4, 'Count Posts TOTAL')
        sheet.write(0, 5, 'Date Most recent post')
        sheet.write(0, 6, 'Date 5th Most recent post')

        pages_data = load_from_mongo(mongo_db="facebook", mongo_db_coll="pages_info")  # collection where all
                                                                                       # the data for each page is stored
        pages_data = facebook_sort_pages(pages_data, "DESC")
        i = 1  # index for rows in sheet
        for page in pages_data:
            id = page['id']
            sheet.write(i, 0, page['name'])
            sheet.write(i, 1, page['likes'])
            sheet.write(i, 2, page['talking_about_count'])

            most_recent_post = 0
            fifth_most_recent_post = 0
            result = facebook_get_posts_from_database(from_user=page['name'], page_name=page['name'], limit=5)
            if result:
                most_recent_post = result[0]['created_time']
                fifth_most_recent_post = result[len(result)-1]['created_time'] # some pages have less than 5 posts
            sheet.write(i, 5, most_recent_post)
            sheet.write(i, 6, fifth_most_recent_post)

            monthly_posts = len(facebook_get_posts_for_month(page['name'], month="07"))
            if monthly_posts is None:
                monthly_posts = 0
            sheet.write(i, 3, monthly_posts)

            total_posts = 0
            result = facebook_get_posts_from_database(from_user=page['name'], page_name=page['name'])
            if result:
                total_posts = len(result)
            sheet.write(i, 4, total_posts)

            i += 1
        workbook.save(facebook_path_to_EXPORT_FILE)

    elif action == '9':
        page_id = "173685876111989"  # sample id
        facebook_print_page_insights(access_token, page_id)

    elif action == '10':
        page_id = "173685876111989"
        page_data = facebook_get_page_data(access_token, page_id)
        if page_data:
            monthly_posts = facebook_get_posts_for_month(page_data['name'], month="07")
            print page_data['name'], " : ", len(monthly_posts)
            for post in monthly_posts:
                print post










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
            print "5. Call function for saving tweets from list members on interval( predefined for community-council)"
            print "6. Get list members"
            print "7. Search & save tweets for a specific query"
            print "8. Search & save tweets from the streaming api"
            print "9. Get all tweets from a user's timeline"
            print "10. Print common entities"
            print "11. Get list members"
            print "12. MULTIGRAPH"
            print "13. find  popular tweets from list of tweets"
            print "14. Get twitter info about a specific user"
            print "15. Get date for last tweet"
            print "16. Get date for fifth tweet"

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
            hashtags = twitter_get_hashtags_from_tweets(results)
            print "num of hashtags: ", len(hashtags)
            for hashtag in hashtags:
                print "#", hashtag


        elif action == '2': # create & export graph of members of twitter list and their followers
            #create directed graph of members of a list and their followers
            #save list of followers for each member into a separate collection named after the slug ending with  _member
            slug="community-councils"
            graph = create_directed_graph_of_list_members_and_followers(slug)
            export_graph_to_gml(graph,path_to_graph_file)



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
                # screen_name = raw_input('Enter the screen name: ').strip()
                # while not screen_name:
                #     screen_name = raw_input('Enter a query:').strip()
                # debug_print("Getting tweets from user: " + screen_name + " ... ")
                screen_name = "spartakan"
                tweets = twitter_user_timeline(api, screen_name=screen_name)


        elif action == '10':
                results = load_from_mongo("twitter", "#indyref")
                common_entities = get_common_tweet_entities(results)
                print_prettytable(common_entities)

        elif action == '11':  # get list members
            twitter_get_list_members(api)

        elif action == '12':
            print "MULTIGRAPH"
            slug = "community-councils"
            mdG = create_multi_graph_of_list_memebers_and_followers(api,slug)
            export_graph_to_gml(mdG, "C:/Users/Windows/Desktop/twitterAnalyzer/CrawlingModule/Resources/twitter_multigraph1.gml")


        elif action == '13':  # find popular tweets from list of tweets
            statuses = load_from_mongo("twitter", "community-councils")
            find_popular_tweets(statuses=statuses)

        elif action == '14':  # get info for user
            screen_name = "spartakan"
            user = twitter_get_user_info(api, screen_name)
            debug_print(json.dumps(user, indent=1))

        elif action == '15':
            screen_name = "spartakan"
            print twitter_date_of_last_tweet(screen_name)

        elif action == '16':
           screen_name = "spartakan"
           print twitter_date_of_fifth_tweet(screen_name)

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




