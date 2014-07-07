import tweepy
import twitter
import json
import os
import platform
import logging
from twitter.oauth import read_token_file, write_token_file


logger = logging.getLogger(__name__)
#to print info messages debug must be true!
debug = True

def setup_logging():
    """
    Initializing the logging system used to write errors to a log file
    """
    #ceating a file handler
    #logging.basicConfig()
    if platform.system() == 'Windows':
        LOG_FILE = os.path.expanduser("H:/twitterAnalyzer/CrawlingModule/Resources/error.log").replace("\\", "/")
    elif platform.system() == 'Linux':
        LOG_FILE = os.path.abspath(os.path.expanduser("~/twitterAnalyzer/CrawlingModule/Resources/error.log"))
    handler = logging.FileHandler(LOG_FILE)
    handler.setLevel(logging.ERROR)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)


def oauth_login():
    """
    Authorize the application to access the user's profile
    using twitter's API v1.1's Authentication Model (oAuth dance)
    :returns twitter_api
    :libraries tweepy, twitter
    """
    CONSUMER_KEY = 'hiXJndRNsYmzrpI9CWmeCJ3r5'
    CONSUMER_SECRET = 'pEs9mzbqeYwl2Ax9OtYPtFowgK6DdTgraZqTPG8Sc2nbID0PIk'
    OAUTH_FILE = ''
    if debug:
        print 'INFO: Executing oauth_login() method ... '
        print 'INFO: Checking operating system : ', platform.system()

    #Check on which operating system is the script running
    if platform.system() == 'Windows':
        OAUTH_FILE = os.path.expanduser("H:/twitterAnalyzer/CrawlingModule/Resources/twitter_oauth.txt").replace("\\", "/")
    elif platform.system() == 'Linux':
        OAUTH_FILE = os.path.abspath(os.path.expanduser("~/twitterAnalyzer/CrawlingModule/Resources/twitter_oauth.txt"))


    #Read the access token from a file
    try:
        oauth_token, oauth_token_secret = read_token_file(OAUTH_FILE)
    except Exception, e:
        if debug:
            print "INFO: IOError: File ", OAUTH_FILE, "not found!"
            logger.error('Failed to open file', exc_info=True)
    else:
        #Check if the reading from the file has been successful and try to authorize with that access token
        if oauth_token and oauth_token_secret:
            try:
                oauth = twitter.oauth.OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET)
            except Exception, e:
                logger.error('Failed request', exc_info=True)
            else:
                if debug:
                    print "INFO: Read Access Token from file"
                twitter_api = twitter.Twitter(auth=oauth)
                return twitter_api
        #The access token isn't in the file so try to obtain him
        else:
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.secure = True
            auth_url = auth.get_authorization_url()
            print 'Please authorize: ' + auth_url
            verifier = raw_input('PIN: ').strip()
            try:
                auth.get_access_token(verifier)
            except Exception, e:
                logger.error('Failed request', exc_info=True)
            else:
                if debug:
                    print "INFO: GET ACCESS_KEY = '%s'" % auth.access_token.key
                    print "INFO: GET ACCESS_SECRET = '%s'" % auth.access_token.secret
                ACCESS_KEY = auth.access_token.key
                ACCESS_SECRET = auth.access_token.secret
                write_token_file(OAUTH_FILE, ACCESS_KEY, ACCESS_SECRET)
                oauth = twitter.oauth.OAuth(ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
                twitter_api = twitter.Twitter(auth=oauth)
                return twitter_api
    return False

def twitter_search(twitter_api, q, max_results=200, **kw):
    """
    Search tweets for a given query
    description of parametars: https://dev.twitter.com/docs/api/1.1/get/search/tweets
    Warning: OAuth users can "only" make 180 search queries per 15-minute interval.
     :param twitter_api
     :param q
     :param max_results
     :param kw
     """
    if debug:
        print 'INFO: Executing twitter_search() method ...  '

    #Get a collection of relevant Tweets matching a specified query
    try:
        search_results = twitter_api.search.tweets(q=q, count=100, **kw)
        statuses = search_results['statuses']
        if debug:
            print "INFO : number of statuses: ", len(statuses)
    except Exception, e:
        logger.error('Failed request', exc_info=True)
        return False
    else:
        max_results = min(1000, max_results)
        # Iterate through 5 more batches of results by following the cursor
        for _ in range(10):  # 10*100 = 1000
            try:
                next_results = search_results['search_metadata']['next_results']
            except KeyError, e:
                logger.error('Failed to find attribute '
                             + '(WARRNING: might throw this exception '
                             + 'for some results while searching in the loop)'
                             , exc_info=True)
                break
            kwargs = dict([kv.split('=') for kv in next_results[1:].split("&")])
            search_results = twitter_api.search.tweets(**kwargs)
            statuses += search_results['statuses']
            if len(statuses) > max_results:
                break
        return statuses

def main():
    setup_logging()
    api = oauth_login()
    if api:
        if debug:
            print "INFO: Successfully authenticated and authorized"
            print "Read How to build a query first ! ( https://dev.twitter.com/docs/using-search )  "
        q = raw_input('Enter a query: ').strip()
        results = twitter_search(api, q, max_results=10)
        #check if results for that query are found
        if results: # Show one sample search result by slicing the list...
            print "Result: ", json.dumps(results[0], indent=1)
            if debug:
                print "INFO: Count for query( \'", q, "\' ) : ", len(results)
        else:
            print "INFO: No results for :", q

if __name__ == '__main__':
    main()
