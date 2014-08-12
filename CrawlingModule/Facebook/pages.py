import requests  # pip install requests
import json
import xlrd  # pip install xlrd
from config import *
from CrawlingModule.Facebook.authorization import facebook_authorize
from DatabaseModule.FacebookWrapper.database_manipulation import facebook_save_to_mongo

def facebook_get_page_posts(ACCESS_TOKEN, page_id=None, limit=100):

    if page_id:
        base_url = 'https://graph.facebook.com/'+page_id+"/posts"
        fields = ''
        #url = '%s?fields=%s&access_token=%s' % (base_url.strip(), fields, ACCESS_TOKEN)
        url = '%s?access_token=%s' % (base_url.strip(), ACCESS_TOKEN)
        print url
        result = []
        content = requests.get(url).json()
        num_results=len(content["data"])
        if num_results >= limit :
            return content["data"]

        result = content["data"]
        i=0
        #call for the rest of the posts
        while True:

            try:
                next = content["paging"]["next"]
                print("next: ",next)
                content = requests.get(next).json()
                result += content["data"]

            except Exception, e: # no next result
                print e.message
                break
            if len(result)>= limit:
                    break
        return result #json.dumps(content, indent=1)


def facebook_get_page_data(access_token, name):
    base_url = 'https://graph.facebook.com/'+name
    #fields = 'id,name,likes,talking_about_count'
    fields = ''
    url = '%s?include_hidden=true&fields=%s&access_token=%s' % (base_url.strip(), fields, access_token)
    #print url
    # Interpret the response as JSON and convert back
    # to Python data structures
    content = None
    try:
        content = requests.get(url).json()
        if content["name"]:
            pass
    #if the content is not a page
    except KeyError, e:
        pass
    else:
        return content



def facebook_sort_pages(pages, order="DESC"):
    """ Sorts the list of pages first by number of likes then by number of people talking about it
    :parameter pages - list of pages to sort
    :parameter order - order in which the list should be sorted. values: ASC and DESC
    :returns pages - sorted ist of pages
    """
    #debug_print("EXEC facebook_sort_pages method :")
    #print pages
    #sort statuses by likes, then by num of people talking about it
    if order == "DESC":
        for i in range(0, len(pages)):
            for j in range(i, len(pages)):
                if int(pages[i]['likes']) < int(pages[j]['likes']):
                    pages[i], pages[j] = pages[j], pages[i]
                elif int(pages[i]['likes']) == int(pages[j]['likes']):
                    if int(pages[i]['talking_about_count']) < int(pages[j]['talking_about_count']):
                        pages[i], pages[j] = pages[j], pages[i]
    elif order == "ASC":
         for i in range(0, len(pages)):
            for j in range(i, len(pages)):
                if int(pages[i]['likes']) > int(pages[j]['likes']):
                    pages[i], pages[j] = pages[j], pages[i]
                elif int(pages[i]['likes']) == int(pages[j]['likes']):
                    if int(pages[i]['talking_about_count']) > int(pages[j]['talking_about_count']):
                        pages[i], pages[j] = pages[j], pages[i]
    return pages


def facebook_read_pages_from_excel(access_token, file=facebook_path_to_PAGES_FILE):

    """ This function is custom made for a specific excel file, modify it for further use
    :param file
    :returns pages - dictionary of pages and their facebook data
    """
    workbook = xlrd.open_workbook(filename=file)  # get all facebook links from excel file
    sheet = workbook.sheet_by_index(0)  # get the 0 sheet
    pages = []
    debug_print("Reading pages' names from file. Might take few minutes...")

    for cell in sheet.col_values(colx=3):  # read column number 3
        parts = cell.split("?")   # split URLs that look like
                                                            # https://www.facebook.com/RoseheartyCommunityCouncil     or
                                                        # https://www.facebook.com/pages/RoseheartyCommunityCouncil   or
                                                # https://www.facebook.com/pages/Alloa-Community-Council/514111341975813

        base = parts[0]  # get the base of the url if it contains parameters after a ?
        url_parts = base.split("/")
        last = url_parts[len(url_parts)-1]  # get the name or id whichever one is last
        page = None
        if last:
            page = facebook_get_page_data(access_token, last+"")  # id might be integer
        if page is not None:
            pages.append(dict(page))  # add to dictionary of pages and their facebook data in json format

    return pages

def facebook_print_page_data(pages=None):
    if pages is not None:
        pages = facebook_sort_pages(pages)
        print '{0:10}     {1:10}     {2:20} '.format("Likes", "Talking about", "Page")
        for i in range(0, len(pages)):
            print '{0:10}     {1:10}     {2:20} '.format(pages[i]['likes'], pages[i]['talking_about_count'], pages[i]['name'])


def facebook_save_posts(page, posts):
    """Saves posts for pages into mongo. The name od the page is the collection and facebook is the database
    :param page - name of collection
    :param posts - data to be saved
    """
    facebook_save_to_mongo(mongo_db="facebook", mongo_db_coll=page, data=posts)

