import os
import platform
import sys
import logging
from debugging_setup import setup_logging, debug_print
#This file is included in every module/script

#set system path
if platform.system() == 'Windows':
    if os.path.exists("H:/SocialNetworkAnalyzer"):
        sys.path.append(os.path.abspath("H:/SocialNetworkAnalyzer"))
    elif os.path.exists("C:/Users/Windows/Desktop/SocialNetworkAnalyzer"):
        sys.path.append(os.path.abspath("C:/Users/Windows/Desktop/SocialNetworkAnalyzer"))
elif platform.system() == 'Linux':
    sys.path.insert(0,os.path.abspath("/home/sd/SocialNetworkAnalyzer"))
    print "SYS PATH : ",sys.path
    #sys.path.append(os.path.abspath("~/SocialNetworkAnalyzer"))
  #Check on which operating system the script is running and get the file from that path


#Consumer key & secret for facebook authorization
facebook_CONSUMER_ID = "<your facebook consumer id here>"
facebook_CONSUMER_SECRET = "<your facebook consumer secret here>"



#determine path for files based on the computer you're using
facebook_path_to_PAGES_FILE = ""  #list with pages for community councils
facebook_path_to_EXPORT_FILE = ""

if platform.system() == "Windows":
    if os.path.exists("H:/SocialNetworkAnalyzer/Resources/CC Social media (1).xlsx"):
        facebook_path_to_PAGES_FILE="H:/SocialNetworkAnalyzer/Resources/CC Social media (1).xlsx"
        facebook_path_to_EXPORT_FILE="H:/SocialNetworkAnalyzer/Resources/Facebook_analysis.xls"
        debug_print("  Path exists: %s"%facebook_path_to_PAGES_FILE)

    elif os.path.exists("C:/Users/Windows/Desktop/SocialNetworkAnalyzer/Resources/CC Social media.xlsx"):
        facebook_path_to_PAGES_FILE = "C:/Users/Windows/Desktop/SocialNetworkAnalyzer/Resources/CC Social media.xlsx"
        facebook_path_to_EXPORT_FILE = "C:/Users/Windows/Desktop/SocialNetworkAnalyzer/Resources/Facebook_analysis.xls"
        debug_print("  Path exists: %s" % facebook_path_to_PAGES_FILE)

    else:
        debug_print("  Path Not Found!")
elif platform.system() == 'Linux':
    facebook_path_to_PAGES_FILE = "/home/sd/SocialNetworkAnalyzer/Resources/Facebook_analysis.xlsx"
    facebook_path_to_EXPORT_FILE = "/home/sd/SocialNetworkAnalyzer/Resources/Facebook_analysis.xls"



#ONLY FOR WINDOWS
#Consumer key & secret from https://apps.twitter.com/ for twitter authorization
path_to_graph_file = "c:/data/graph_community-councils.gml" #where to export the .gml file


twitter_CONSUMER_KEY = '<your twitter consumer hey here>'
twitter_CONSUMER_SECRET = '<your twitter consumer secret here>'
twitter_OAUTH_FILE = ''
if platform.system() == 'Windows':
    if os.path.exists("H:/SocialNetworkAnalyzer/CrawlingModule/Resources/twitter_oauth.txt"):
        twitter_OAUTH_FILE = os.path.expanduser("H:/SocialNetworkAnalyzer/Resources/twitter_oauth.txt").replace("\\", "/")
    if os.path.exists("C:/Users/Windows/Desktop/SocialNetworkAnalyzer/Resources/twitter_oauth.txt"):
        twitter_OAUTH_FILE = os.path.expanduser("C:/Users/Windows/Desktop/SocialNetworkAnalyzer/Resources/twitter_oauth.txt").replace("\\", "/")
elif platform.system() == 'Linux':
    twitter_OAUTH_FILE = os.path.abspath(os.path.expanduser("~/SocialNetworkAnalyzer/Resources/twitter_oauth.txt"))

