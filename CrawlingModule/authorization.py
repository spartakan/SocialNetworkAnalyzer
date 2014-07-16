import tweepy
import twitter
import os
import sys
import platform
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from twitter.oauth import read_token_file, write_token_file
print sys.path
from debugging_setup import setup_logging, debug_print


logger = setup_logging()

def oauth_login():
    """
    Authorize the application to access the user's profile
    using twitter's API v1.1's Authentication Model (oAuth dance)
    If the application is being authorized for the first time, the access key & secret are saved into a file
    and with every other execution of the script, the access token & secret are read from the oauth file.
    :returns twitter_api
    :libraries tweepy, twitter
    """
    CONSUMER_KEY = 'hiXJndRNsYmzrpI9CWmeCJ3r5'
    CONSUMER_SECRET = 'pEs9mzbqeYwl2Ax9OtYPtFowgK6DdTgraZqTPG8Sc2nbID0PIk'
    OAUTH_FILE = ''
    debug_print('Executing oauth_login() method ... ')
    debug_print(' Checking operating system : '+ platform.system())

    #Check on which operating system is the script running
    if platform.system() == 'Windows':
        OAUTH_FILE = os.path.expanduser("H:/twitterAnalyzer/CrawlingModule/Resources/twitter_oauth.txt").replace("\\", "/")
    elif platform.system() == 'Linux':
        OAUTH_FILE = os.path.abspath(os.path.expanduser("~/twitterAnalyzer/CrawlingModule/Resources/twitter_oauth.txt"))

    #Read the access token from a file
    try:
        oauth_token, oauth_token_secret = read_token_file(OAUTH_FILE)
    except Exception, e:
            debug_print("IOError: File " + OAUTH_FILE + "not found!")
            logger.error('Failed to open file', exc_info=True)
    else:
        #Check if the reading from the file has been successful and try to authorize with that access token
        if oauth_token and oauth_token_secret:
            try:
                oauth = twitter.oauth.OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET)
            except Exception, e:
                logger.error('Failed request', exc_info=True)
            else:
                debug_print("Read Access Token from file")
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
                debug_print("GET ACCESS_KEY = " + auth.access_token.key)
                debug_print("GET ACCESS_SECRET = " + auth.access_token.secret)
                ACCESS_KEY = auth.access_token.key
                ACCESS_SECRET = auth.access_token.secret
                write_token_file(OAUTH_FILE, ACCESS_KEY, ACCESS_SECRET)
                oauth = twitter.oauth.OAuth(ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
                twitter_api = twitter.Twitter(auth=oauth)
                return twitter_api
    return False


