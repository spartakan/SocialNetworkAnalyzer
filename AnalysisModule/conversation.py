import logging, os, sys, platform, re
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from collections import Counter
from prettytable import PrettyTable
from debugging_setup import setup_logging, debug_print
import logging
logger = logging.getLogger(__name__)
logger = setup_logging(logger)


def get_replies_for_tweet(api, status):

 print ""
