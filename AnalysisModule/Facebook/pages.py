from config import *
from DatabaseModule.database_manipulation import load_from_mongo, load_from_mongo_sorted
DESC = -1
ASC = 1

def facebook_get_likes_count(page_name):
    """
    Reads from database the number of likes for a page

    :param page_name:
    :return: number of likes
    """
    debug_print("EXEC facebook_get_likes_count method :")
    if page_name is not None:
        criteria = {"name": "%s" % page_name}
        projection = {"likes": 1, "_id": 0}
        result = load_from_mongo(mongo_db="facebook",mongo_db_coll="pages_info", criteria=criteria,projection=projection)

        return result[0]["likes"]


def facebook_get_talkingabout_count(page_name):
    """
    Reads from database the number of the parameter talking about(facebook) for a page

    :param page_name:
    :return: talking_about_count - number of people talking about your page
    """
    debug_print("EXEC facebook_get_talkingabout_count method :")
    if page_name is not None:
        criteria = {"name": "%s" % page_name}
        projection = {"talking_about_count": 1, "_id": 0}
        result = load_from_mongo(mongo_db="facebook",mongo_db_coll="pages_info",criteria=criteria,projection=projection)
        talking_about_count = result[0]["talking_about_count"]
        return talking_about_count


def facebook_get_posts_from_database(from_user=None, page_name=None, limit=None):  # get posts for certain period for certain users/or not
    """
    Reads posts from database writen by a certain user posted on a certain page
    :parameter: from_user - the name of the user that wrote the post
    :parameter: page_name - the name of the page the post was posted to
    :parameter: limit - number of maximum number of posts
    :return: result - posts
    """
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



def facebook_get_posts_for_month(page_name, month):
    """
    Reads posts from database for a given page writen in a certain month.
    Used when looking for a post written in a certain period.

    :parameter: page_name - the name of the page the post was posted to
    :parameter: month - the month the page was created on
    :return: result - posts
    """
    debug_print("EXEC facebook_get_posts_for_month method :")

    regex = "2014-%s-.*" % month  # regex for searching dates in database
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
    debug_print("EXEC facebook_sort_pages method :")
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