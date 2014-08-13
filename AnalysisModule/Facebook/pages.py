from config import *
from DatabaseModule.database_manipulation import load_from_mongo, load_from_mongo_sorted


def facebook_get_likes_count(page_name):

    debug_print("EXEC facebook_get_likes_count method :")
    if page_name is not None:
        criteria = {"name": "%s" % page_name}
        projection = {"likes": 1, "_id": 0}
        result = load_from_mongo(mongo_db="facebook",mongo_db_coll="pages_info", criteria=criteria,projection=projection)

        return result[0]["likes"]


def facebook_get_talkingabout_count(page_name):

    debug_print("EXEC facebook_get_talkingabout_count method :")
    if page_name is not None:
        criteria = {"name": "%s" % page_name}
        projection = {"talking_about_count": 1, "_id": 0}
        result = load_from_mongo(mongo_db="facebook",mongo_db_coll="pages_info",criteria=criteria,projection=projection)

        return result[0]["talking_about_count"]


def facebook_get_posts(date=None, from_user=None, page_name=None):  # get posts for certain period for certain users/or not

    debug_print("EXEC facebook_get_posts method :")
    if from_user is not None:
        criteria = {"from.name": "%s" % from_user}

        #must create a list of sets with [('field',value),('field2',value2)] for multiple sorting parameters
        sort_params = [("created_time", -1)] # sort by DESC order , from latest to older

        result = load_from_mongo_sorted(mongo_db="facebook", mongo_db_coll=page_name, sort_params=sort_params)
        return result


def facebook_get_most_recent_post(page, index=5):  # get fifth most recent post  return date
    print""



