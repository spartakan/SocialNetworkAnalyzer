import tweepy
import twitter
import json
import os
from twitter.oauth import read_token_file, write_token_file
import platform

def oauth_login():
    """
    Authorize the application to access the user's profile
    using twitter's API v1.1's Authentication Model (oAuth dance)
    :returns twitter_api
    :libraries tweepy, twitter
    """
    CONSUMER_KEY = 'hiXJndRNsYmzrpI9CWmeCJ3r5'
    CONSUMER_SECRET = 'pEs9mzbqeYwl2Ax9OtYPtFowgK6DdTgraZqTPG8Sc2nbID0PIk'
    if platform.system() == 'Windows':
        print 'Operating system : ', platform.system()
        OAUTH_FILE = os.path.expanduser("H:/twitterAnalyzer/CrawlingModule/Resources/twitter_oauth.txt").replace("\\", "/")
    elif platform.system() == 'Linux':
        print 'Operating system : ', platform.system()
        OAUTH_FILE = os.path.abspath(os.path.expanduser("~/twitterAnalyzer//CrawlingModule/Resources/twitter_oauth.txt"))

    #read the access token from a file
    oauth_token, oauth_token_secret = read_token_file(OAUTH_FILE)

    #check if the reading from the file has been successful and continue with the authorization
    if oauth_token and oauth_token_secret:
        oauth = twitter.oauth.OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET)
        print "ACCESS TOKEN READ from file!"

    else:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.secure = True
        auth_url = auth.get_authorization_url()
        print 'Please authorize: ' + auth_url
        verifier = raw_input('PIN: ').strip()
        auth.get_access_token(verifier)
        print "ACCESS_KEY = '%s'" % auth.access_token.key
        print "ACCESS_SECRET = '%s'" % auth.access_token.secret
        ACCESS_KEY = auth.access_token.key
        ACCESS_SECRET = auth.access_token.secret
        write_token_file(OAUTH_FILE, ACCESS_KEY, ACCESS_SECRET)
        oauth = twitter.oauth.OAuth(ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
        print "ACCESS TOKEN ACQUIRED for the first time!"

    twitter_api = twitter.Twitter(auth=oauth)
    return twitter_api



def twitter_search(twitter_api, q, max_results=200, **kw):
    """
    Search tweets for a given query
     :param twitter_api
     :param q
     :param max_results
     :param kw
     """
    search_results = twitter_api.search.tweets(q=q, count=100, **kw)
    statuses = search_results['statuses']
    max_results = min(1000, max_results)
    for _ in range(10):  # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError, e:
            print "Error: No more results when next_results doesn't exist"
            break
        else:
            kwargs = dict([kv.split('=') for kv in next_results[1:].split("&")])
            search_results = twitter_api.search.tweets(**kwargs)
            statuses += search_results['statuses']
            if len(statuses) > max_results:
                break
            return statuses


# Sample usage
api = oauth_login()
print "Read How to build a query first ! ( https://dev.twitter.com/docs/using-search )  "
q = raw_input('Enter a query: ').strip()
results = twitter_search(api, q, max_results=10)

#check if results for that query are found
if results: # Show one sample search result by slicing the list...
    print json.dumps(results[0], indent=1)
    print "Count for query( ", q, " ) : ", len(results)
else:
    print "No results for :", q