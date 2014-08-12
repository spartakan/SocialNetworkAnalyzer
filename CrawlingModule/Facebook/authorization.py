import requests
from config import *


def facebook_authorize():
    """
    Authorizes user using facebook graph API
    :returns ACCESS_TOKEN
    """
    oauth_url = "https://graph.facebook.com/oauth/access_token?client_secret="+facebook_CONSUMER_SECRET+"&client_id="+facebook_CONSUMER_ID+"&grant_type=client_credentials"
    result = requests.get(oauth_url)
    debug_print(result.text)  #print the oauth_token
    result = result.text.split("=")
    print result[1]
    ACCESS_TOKEN = result[1]
    return ACCESS_TOKEN
