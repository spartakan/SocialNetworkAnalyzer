import requests  # pip install requests
import json
import xlrd  # pip install xlrd  exports files into xls format
from config import *
from AnalysisModule.Facebook.pages import facebook_sort_pages
from DatabaseModule.database_manipulation import save_to_mongo


def facebook_get_page_posts(ACCESS_TOKEN, page_id=None, limit=1000):
    """
     Getting facebook posts from facebook api for a given page id
     :parameter: ACCESS_TOKEN
     :parameter: page_id

    """
    debug_print("EXEC facebook_get_page_posts method :")
    if page_id:
        base_url = 'https://graph.facebook.com/'+page_id+"/posts"
        fields = ''
        url = '%s?fields=%s&access_token=%s' % (base_url.strip(), fields, ACCESS_TOKEN)
        debug_print("  url: %s"%url)
        result = []
        content = requests.get(url).json()
        num_results = len(content["data"])
        if num_results >= limit:
            return content["data"]

        result = content["data"]
        #call for the rest of the posts
        while True:

            try:
                next = content["paging"]["next"] #if the json file contains paging and next inside paging go to next results
                content = requests.get(next).json()
                result += content["data"] # if there are results save the data

            except Exception, e: # no next result
                print e.message
                break
            if len(result) >= limit:
                    break
        return result  # json.dumps(content, indent=1)


def facebook_get_page_data(access_token, name):

    debug_print("EXEC facebook_get_page_data method :")

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






def facebook_read_pages_from_excel(access_token, file=facebook_path_to_PAGES_FILE):

    """ This function is custom made for a specific excel file, modify it for further use
    :param file - path to file
    :returns pages - array of pages' names or ids
    """
    debug_print("EXEC facebook_read_pages_from_excel method :")
    workbook = xlrd.open_workbook(filename=file)  # get all facebook links from excel file
    sheet = workbook.sheet_by_index(0)  # get the 0 sheet
    pages = []
    debug_print("  Reading pages' names from file. Might take few minutes...")

    for cell in sheet.col_values(colx=3):  # read column number 3
        parts = cell.split("?")   # split URLs that look like:
                                                            # https://www.facebook.com/RoseheartyCommunityCouncil     or
                                                        # https://www.facebook.com/pages/RoseheartyCommunityCouncil   or
                                                # https://www.facebook.com/pages/Alloa-Community-Council/514111341975813

        base = parts[0]  # get the base of the url if it contains parameters after a ?
        base = base.replace("/info","") # remove any /info parts from the urls
        url_parts = base.split("/")
        page_name_or_id = None
        page_name_or_id = url_parts[len(url_parts)-1]  # get the name or id whichever one is last

        if len(page_name_or_id) > 1:
            debug_print("  page name or id: %s" % page_name_or_id)
            pages.append(page_name_or_id)  # add to dictionary of pages and their facebook data in json format
    return pages





def facebook_print_page_data(pages=None):
    """
    Pretty print some data for list of pages
    :param pages: list
    """
    debug_print("EXEC facebook_print_page_data method :")
    if pages is not None:
        pages = facebook_sort_pages(pages)
        print '{0:10}     {1:10}     {2:20} '.format("Likes", "Talking about", "Page")
        for i in range(0, len(pages)):
            print '{0:10}     {1:10}     {2:20} '.format(pages[i]['likes'], pages[i]['talking_about_count'], pages[i]['name'])


def facebook_print_page_insights(access_token, id):
    """
    Print insights for a page
    :param access_token:
    :param id: id of page
    :return:
    """

    debug_print("EXEC facebook_get_page_stories method :")
    base_url = "https://graph.facebook.com/"+id+"/insights"
    fields = "period=month"
    url = '%s?access_token=%s' % (base_url.strip(), access_token)
    #print url
    # Interpret the response as JSON and convert back
    # to Python data structures
    content = None
    try:
        content = requests.get(url).json()
        #if content["name"]:
            #pass
    #if the content is not a page
    except KeyError, e:
        pass
    else:
        #return content
        print json.dumps(content, indent=1)

