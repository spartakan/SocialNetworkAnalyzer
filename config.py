import os
import platform
import sys
import logging
from debugging_setup import setup_logging, debug_print
#This file is included in every module/script

#set system path
if platform.system() == 'Windows':
    if os.path.exists("~/SocialNetworkAnalyzer"):
        sys.path.append(os.path.abspath("~/SocialNetworkAnalyzer"))
   
elif platform.system() == 'Linux':
    sys.path.insert(0,os.path.abspath("~/SocialNetworkAnalyzer"))



#Consumer key & secret for facebook authorization
facebook_CONSUMER_ID = "<your facebook consumer id here>"
facebook_CONSUMER_SECRET = "<your facebook consumer secret here>"



#determine path for files based on the computer you're using
facebook_path_to_PAGES_FILE = ""  #list with pages for community councils
facebook_path_to_EXPORT_FILE = ""
twitter_path_to_EXPORT_FILE = ""

if platform.system() == "Windows":
    if os.path.exists():
        facebook_path_to_PAGES_FILE=
        facebook_path_to_EXPORT_FILE=
        twitter_path_to_EXPORT_FILE=  

        debug_print("  Path exists: %s"%facebook_path_to_PAGES_FILE)

    elif os.path.exists( ):
        facebook_path_to_PAGES_FILE = ""
        facebook_path_to_EXPORT_FILE = ""
        twitter_path_to_EXPORT_FILE = 
        debug_print("  Path exists: %s" % facebook_path_to_PAGES_FILE)

    else:
        debug_print("  Path Not Found!")
elif platform.system() == 'Linux':
    facebook_path_to_PAGES_FILE =   ""   #official facebook pages 
    facebook_path_to_EXPORT_FILE = ""
    twitter_path_to_EXPORT_FILE = ""



#ONLY FOR WINDOWS
#Consumer key & secret from https://apps.twitter.com/ for twitter authorization
path_to_graph_file= ''
#path_to_graph_file = '' #where to export the .gml file for windows

twitter_CONSUMER_KEY = '<your twitter consumer secret here>'
twitter_CONSUMER_SECRET =  '<your twitter consumer secret here>'
twitter_OAUTH_FILE = ' <path to file with authorization credentials>' #initialize

#Create a Resources folder and save the oauth file there!!!

if platform.system() == 'Windows':
    if os.path.exists("~/SocialNetworkAnalyzer/CrawlingModule/Resources/twitter_oauth.txt"):
        twitter_OAUTH_FILE = os.path.expanduser("~/SocialNetworkAnalyzer/Resources/twitter_oauth.txt").replace("\\", "/")
  
elif platform.system() == 'Linux':
    twitter_OAUTH_FILE = os.path.abspath(os.path.expanduser("~/SocialNetworkAnalyzer/Resources/twitter_oauth.txt"))





SNEZEeeeeeeeeeeee