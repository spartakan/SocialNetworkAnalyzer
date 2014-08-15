from config import *
from DatabaseModule.database_manipulation import load_from_mongo, load_from_mongo_sorted
DESC = -1
ASC = 1

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


def facebook_get_posts_from_database(from_user=None, page_name=None, limit=None):  # get posts for certain period for certain users/or not

    debug_print("EXEC facebook_get_posts_from_database method :")
    if from_user is not None:
        criteria = {"from.name": from_user}
    else:
        criteria = None
        #must create a list of sets with [('field',value),('field2',value2)] for multiple sorting parameters
    sort_params = [("created_time", -1)] # sort by DESC order , from latest to older

    result = load_from_mongo_sorted(mongo_db="facebook", mongo_db_coll=page_name, sort_params=sort_params, limit=limit, criteria=criteria)
    #print("res: form data ", result)
    return result



def facebook_get_posts_for_month(page_name, month="07"):
    regex = "2014-%s-.*" % month  # query for searching dates in database
    criteria = {"created_time": {"$regex": regex}}

    #must create a list of sets with [('field',value),('field2',value2)] for multiple sorting parameters
    sort_params = [("created_time", -1)]  # sort by DESC order , from latest to older

    result = load_from_mongo_sorted(mongo_db="facebook", mongo_db_coll=page_name, sort_params=sort_params, criteria=criteria)
    return result



def facebook_sort_pages(pages, order=DESC):
    """ Sorts the list of pages first by number of likes then by number of people talking about it
    :parameter pages - list of pages to sort
    :parameter order - order in which the list should be sorted. values: ASC and DESC
    :returns pages - sorted ist of pages
    """
    #debug_print("EXEC facebook_sort_pages method :")
    #print pages
    #sort statuses by likes, then by num of people talking about it
    if order == DESC:
        for i in range(0, len(pages)):
            for j in range(i, len(pages)):
                if int(pages[i]['likes']) < int(pages[j]['likes']):
                    pages[i], pages[j] = pages[j], pages[i]
                elif int(pages[i]['likes']) == int(pages[j]['likes']):
                    if int(pages[i]['talking_about_count']) < int(pages[j]['talking_about_count']):
                        pages[i], pages[j] = pages[j], pages[i]
    elif order == ASC:
         for i in range(0, len(pages)):
            for j in range(i, len(pages)):
                if int(pages[i]['likes']) > int(pages[j]['likes']):
                    pages[i], pages[j] = pages[j], pages[i]
                elif int(pages[i]['likes']) == int(pages[j]['likes']):
                    if int(pages[i]['talking_about_count']) > int(pages[j]['talking_about_count']):
                        pages[i], pages[j] = pages[j], pages[i]
    return pages