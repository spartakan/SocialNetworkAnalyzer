import os
import platform
import sys
import logging
from debugging_setup import setup_logging, debug_print

#set system path
if platform.system() == 'Windows':
    sys.path.append(os.path.abspath("H:/twitterAnalyzer"))
elif platform.system() == 'Linux':
    sys.path.insert(0,os.path.abspath("/home/sd/twitterAnalyzer"))
    print "SYS PATH : ",sys.path
    #sys.path.append(os.path.abspath("~/twitterAnalyzer"))
  #Check on which operating system the script is running and get the file from that path


#Consumer key & secret for facebook
facebook_CONSUMER_ID = "784369068293517"
facebook_CONSUMER_SECRET = "d309eff5bcd6a6d02cc8602b2ba9e438"


#Consumer key & secret from https://apps.twitter.com/ for twitter authorization
twitter_CONSUMER_KEY = 'hiXJndRNsYmzrpI9CWmeCJ3r5'
twitter_CONSUMER_SECRET = 'pEs9mzbqeYwl2Ax9OtYPtFowgK6DdTgraZqTPG8Sc2nbID0PIk'
twitter_OAUTH_FILE = ''
if platform.system() == 'Windows':
    twitter_OAUTH_FILE = os.path.expanduser("H:/twitterAnalyzer/CrawlingModule/Resources/twitter_oauth.txt").replace("\\", "/")
elif platform.system() == 'Linux':
    twitter_OAUTH_FILE = os.path.abspath(os.path.expanduser("~/twitterAnalyzer/CrawlingModule/Resources/twitter_oauth.txt"))