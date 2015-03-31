
import tweepy, twitter
#from twitter.oauth import read_token_file, write_token_file
from config import *  # OAUTH FILE, CONSUMER SECRET/KEY, logging setup

#create a logger for this module , set it up, and use it to write errors to file
logger = logging.getLogger(__name__)
logger = setup_logging(logger)


def twitter_authorize():
    """
    Authorize the application to access the user's profile
    using twitter's API v1.1's Authentication Model (oAuth dance)
    If the application is being authorized for the first time, the access key & secret are saved into a file
    and with every other execution of the script, the access token & secret are read from the oauth file.
    :returns twitter_api
    """

    debug_print("EXEC twitter_authorize method :")
    debug_print("  Authorizing...")
    debug_print("  Checking operating system : %s  ; for file's path " % platform.system())

    #get authorization with the access token from file
    if twitter_oauth_token and twitter_oauth_secret:
        try:
            oauth = twitter.oauth.OAuth(twitter_oauth_token, twitter_oauth_secret, twitter_CONSUMER_KEY, twitter_CONSUMER_SECRET)
        except Exception, e: # can't twitter_authorize
            debug_print("  %s" % e.message)
            logger.error(e.message)
        else:  # authorized
            debug_print("Access Token from SETTINGS...")
            debug_print("GET ACCESS_KEY = " + twitter_oauth_token)
            debug_print("GET ACCESS_SECRET = " + twitter_oauth_secret)

            twitter_api = twitter.Twitter(auth=oauth)
            print "API: ",twitter_api
            return twitter_api

    return False


