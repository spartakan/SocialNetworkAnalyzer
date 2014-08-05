import requests # pip install requests
import json
import xlrd
from debugging_setup import setup_logging, debug_print


def authorize():
    oauth_url = "https://graph.facebook.com/oauth/access_token?client_secret=d309eff5bcd6a6d02cc8602b2ba9e438&client_id=784369068293517&grant_type=client_credentials"
    result = requests.get(oauth_url)
    print result.text
    result = result.text.split("=")
    print result[1]
    ACCESS_TOKEN = result[1]
    return ACCESS_TOKEN

def get_data(ACCESS_TOKEN, name):
    base_url = 'https://graph.facebook.com/'+name
    #fields = 'id,name,likes,talking_about_count'
    fields = ''
    url = '%s?fields=%s&access_token=%s' % (base_url.strip(), fields, ACCESS_TOKEN)
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


def sort_pages(pages, order="DESC"):
    """ Sorts the list of statuses first by number of retweets then by number of favorites
    :parameter statuses - list of statuses to sort
    :parameter order - order in which the list should be sorted. values: ASC and DESC
    :returns statuses - sorted ist of statuses
    """
    #debug_print("EXEC sort_pages method :")
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


access_token = authorize()
workbook = xlrd.open_workbook(filename="C:/Users/zz2005/Desktop/CC Social media (1).xlsx")
sheet = workbook.sheet_by_index(0)
pages = []
debug_print("Getting info for pages. Might take few minutes...")
for cell in sheet.col_values(colx=3):
    parts = cell.split("?")
    #base url with the id or name
    base = parts[0]
    #get just the name or id
    url_parts = base.split("/")
    last = url_parts[len(url_parts)-1]
    #print last

    if last:
        page = get_data(access_token, last+"")
        if page is not None:
            pages.append(dict(page))


pages = sort_pages(pages)
#print '{0:10}     {1:10}     {2:20} '.format("Likes", "Talking about", "Page")
for i in range(0,len(pages)):
    #print '{0:10}     {1:10}     {2:20} '.format(pages[i]['likes'], pages[i]['talking_about_count'], pages[i]['name'])
    print pages[i]

