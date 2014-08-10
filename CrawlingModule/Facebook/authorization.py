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
    #return "CAACEdEose0cBAHG4woHZAq2ZAMSZAGoipjJOo8Vy04dJnwYDWvkKQbNz5JoVLnR4YTuIUid2nYCeQbKlZBdE02YsOeZAJfmhzioRfnm0o3GH0ZBXDdvtiOZAlaOR0KJ4lECGR9Or8A5meL39q5gEAaxX6lssl0JUP8lZBp7JnT70b7twUHOCgdeCtJySvgbdDyq0BjY6JbFKbHB2VblrnH1E"
