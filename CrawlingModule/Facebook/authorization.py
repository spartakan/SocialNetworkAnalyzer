import requests
from config import *


def authorize():
    oauth_url = "https://graph.facebook.com/oauth/access_token?client_secret="+facebook_CONSUMER_SECRET+"&client_id="+facebook_CONSUMER_ID+"&grant_type=client_credentials"
    result = requests.get(oauth_url)
    print result.text
    result = result.text.split("=")
    print result[1]
    ACCESS_TOKEN = result[1]
    return ACCESS_TOKEN