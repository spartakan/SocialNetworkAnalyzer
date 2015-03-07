import sys
import os
import platform
import logging
from SETTINGS import *
from config import *

debug=True
logger = logging.getLogger(__name__)
def debug_print(message):
    """
    Prints messages if the debug variable is set to true
    :param message: message to be printed
    :return: none
    """""
    if debug:
        print >> sys.stderr, "INFO| ", message
        print >> sys.stderr.flush()

def setup_logging(logger):
    """
    Initializing the logging system used to write errors to a log file
    """
    global HOME_PATH
   #ceating a file handler
    #logger.level(logging.INFO)
    if platform.system() == 'Windows':
        if os.path.exists("H:/SocialNetworkAnalyzer/Resources/error.log"):
            LOG_FILE = os.path.expanduser("H:/SocialNetworkAnalyzer/Resources/error.log").replace("\\", "/")
        elif os.path.exists("C:/Users/Windows/Desktop/SocialNetworkAnalyzer/Resources/error.log"):
            LOG_FILE = os.path.expanduser("C:/Users/Windows/Desktop/SocialNetworkAnalyzer/Resources/error.log").replace("\\", "/")
    elif platform.system() == 'Linux':
        #LOG_FILE = os.path.abspath(os.path.expanduser("~/SocialNetworkAnalyzer/CrawlingModule/Resources/error.log"))
        LOG_FILE = os.path.abspath(os.path.expanduser(HOME_PATH+"/CrawlingModule/Resources/error.log"))
    handler = logging.FileHandler(LOG_FILE)
    handler.setLevel(logging.ERROR)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    return logger
