
import tweepy, twitter
from twitter.oauth import read_token_file, write_token_file
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

    # Read the access token from a file
    try:
        oauth_token, oauth_token_secret = read_token_file(twitter_OAUTH_FILE)
    except IOError, e:  # failed to open file
            debug_print("  %s" % e.message)
            logger.error(e.message)
    else:  # file opened successful

        #get authorization with the access token from file
        if oauth_token and oauth_token_secret:
            try:
                oauth = twitter.oauth.OAuth(oauth_token, oauth_token_secret, twitter_CONSUMER_KEY, twitter_CONSUMER_SECRET)
            except Exception, e: # can't twitter_authorize
                debug_print("  %s" % e.message)
                logger.error(e.message)
            else:  # authorized
                debug_print("Reading Access Token from file ...")
                twitter_api = twitter.Twitter(auth=oauth)
                return twitter_api

        #No access token in the file, make a request for it
        else:
            auth = tweepy.OAuthHandler(twitter_CONSUMER_KEY, twitter_CONSUMER_SECRET)
            auth.secure = True
            auth_url = auth.get_authorization_url()
            print 'Please twitter_authorize: ' + auth_url
            verifier = raw_input('PIN: ').strip()
            try:
                auth.get_access_token(verifier)
            except Exception, e:  # unsuccessful attempt to get access token
                debug_print("  %s" % e.message)
                logger.error(e.message)
            else:  # successful attempt to get access token
                debug_print("GET ACCESS_KEY = " + auth.access_token.key)
                debug_print("GET ACCESS_SECRET = " + auth.access_token.secret)
                ACCESS_KEY = auth.access_token.key
                ACCESS_SECRET = auth.access_token.secret
                write_token_file(twitter_OAUTH_FILE, ACCESS_KEY, ACCESS_SECRET)

                #get authorization with the new access token
                oauth = twitter.oauth.OAuth(ACCESS_KEY, ACCESS_SECRET, twitter_CONSUMER_KEY, twitter_CONSUMER_SECRET)
                twitter_api = twitter.Twitter(auth=oauth)
                return twitter_api
    return False


