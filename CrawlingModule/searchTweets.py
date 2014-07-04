import tweepy
import twitter
import json

def oauth_login():
    """
    Authorize the application to access the user's profile
    using twitter's API v1.1's Authentication Model (oAuth dance)
    :returns twitter_api
    :libraries tweepy, twitter
    """
    CONSUMER_KEY = 'hiXJndRNsYmzrpI9CWmeCJ3r5'
    CONSUMER_SECRET = 'pEs9mzbqeYwl2Ax9OtYPtFowgK6DdTgraZqTPG8Sc2nbID0PIk'

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

    oauth = twitter.oauth.OAuth(ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
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
            print "No more results when next_results doesn't exist"
            break

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
# Show one sample search result by slicing the list...
print json.dumps(results[0], indent=1)
print "Count for query( ", q," ) : ",len(results)