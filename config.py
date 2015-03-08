import os
import platform
import sys
import logging
from debugging_setup import setup_logging, debug_print

from SETTINGS import *

#This file is included in every module/script

#set system path
if platform.system() == 'Windows':
    if os.path.exists(HOME_PATH):
        #sys.path.append(os.path.abspath("~/SocialNetworkAnalyzer"))
        sys.path.append(os.path.abspath(HOME_PATH))
   
elif platform.system() == 'Linux':
    sys.path.insert(0,os.path.abspath(HOME_PATH))


if platform.system() == "Windows":
    if os.path.exists():
        facebook_path_to_PAGES_FILE= ""
        facebook_path_to_EXPORT_FILE= ""
        twitter_path_to_EXPORT_FILE=  ""

        debug_print("  Path exists: %s"%facebook_path_to_PAGES_FILE)

    elif os.path.exists( ):
        facebook_path_to_PAGES_FILE = ""
        facebook_path_to_EXPORT_FILE = ""
        twitter_path_to_EXPORT_FILE = ""
        debug_print("  Path exists: %s" % facebook_path_to_PAGES_FILE)

    else:
        debug_print("  Path Not Found!")
elif platform.system() == 'Linux':
    facebook_path_to_PAGES_FILE =   ""   #official facebook pages 
    facebook_path_to_EXPORT_FILE = ""
    twitter_path_to_EXPORT_FILE = ""

#Create a Resources folder and save the oauth file there!!!

#if platform.system() == 'Windows':
#    if os.path.exists(HOME_PATH+"/CrawlingModule/Resources/twitter_oauth.txt"):
#        twitter_OAUTH_FILE = os.path.expanduser(HOME_PATH+"/Resources/twitter_oauth.txt").replace("\\", "/")
#  
#elif platform.system() == 'Linux':
#    twitter_OAUTH_FILE = os.path.abspath(os.path.expanduser(HOME_PATH+"/Resources/twitter_oauth.txt"))

