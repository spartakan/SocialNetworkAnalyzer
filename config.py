import os
import platform
import sys
import logging
from debugging_setup import setup_logging, debug_print

#set system path
if platform.system() == 'Windows':
    if os.path.exists("H:/twitterAnalyzer"):
        sys.path.append(os.path.abspath("H:/twitterAnalyzer"))
    elif os.path.exists("C:/Users/Windows/Desktop/twitterAnalyzer"):
        sys.path.append(os.path.abspath("C:/Users/Windows/Desktop/twitterAnalyzer"))
elif platform.system() == 'Linux':
    sys.path.insert(0,os.path.abspath("/home/sd/twitterAnalyzer"))
    print "SYS PATH : ",sys.path
    #sys.path.append(os.path.abspath("~/twitterAnalyzer"))
  #Check on which operating system the script is running and get the file from that path


#Consumer key & secret for facebook
facebook_CONSUMER_ID = "784369068293517"
facebook_CONSUMER_SECRET = "d309eff5bcd6a6d02cc8602b2ba9e438"
facebook_path_to_PAGES_FILE=""
if platform.system()=="Windows":
    if os.path.exists("C:/Users/zz2005/Desktop/CC Social media (1).xlsx"):
        facebook_path_to_PAGES_FILE="C:/Users/zz2005/Desktop/CC Social media (1).xlsx"
        debug_print("  Path exists: %s"%facebook_path_to_PAGES_FILE)
    elif os.path.exists("C:/Users/Windows/Desktop/twitterAnalyzer/CrawlingModule/Resources/CC Social media.xlsx"):
        facebook_path_to_PAGES_FILE="C:/Users/Windows/Desktop/twitterAnalyzer/CrawlingModule/Resources/CC Social media.xlsx"
        debug_print("  Path exists: %s"%facebook_path_to_PAGES_FILE)
    else:
        debug_print("  Path Not Found!")

#Consumer key & secret from https://apps.twitter.com/ for twitter authorization
path_to_graph_file = "c:/data/graph_community-councils.gml" #where to export the .gml file
twitter_CONSUMER_KEY = 'hiXJndRNsYmzrpI9CWmeCJ3r5'
twitter_CONSUMER_SECRET = 'pEs9mzbqeYwl2Ax9OtYPtFowgK6DdTgraZqTPG8Sc2nbID0PIk'
twitter_OAUTH_FILE = ''
if platform.system() == 'Windows':
    if os.path.exists("H:/twitterAnalyzer/CrawlingModule/Resources/twitter_oauth.txt"):
        twitter_OAUTH_FILE = os.path.expanduser("H:/twitterAnalyzer/CrawlingModule/Resources/twitter_oauth.txt").replace("\\", "/")
    if os.path.exists("C:/Users/Windows/Desktop/twitterAnalyzer/CrawlingModule/Resources/twitter_oauth.txt"):
        twitter_OAUTH_FILE = os.path.expanduser("C:/Users/Windows/Desktop/twitterAnalyzer/CrawlingModule/Resources/twitter_oauth.txt").replace("\\", "/")
elif platform.system() == 'Linux':
    twitter_OAUTH_FILE = os.path.abspath(os.path.expanduser("~/twitterAnalyzer/CrawlingModule/Resources/twitter_oauth.txt"))

