import logging, os, sys, platform, re
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from collections import Counter
from prettytable import PrettyTable
from debugging_setup import setup_logging, debug_print
import logging
logger = logging.getLogger(__name__)
logger = setup_logging(logger)


def extract_tweet_entities(statuses):
# See https://dev.twitter.com/docs/tweet-entities for more details on tweet
# entities
    if len(statuses) == 0:
        return [], [], [], [], []
    screen_names = [user_mention['screen_name']
                        for status in statuses
                            for user_mention in status['entities']['user_mentions']]
    hashtags = [hashtag['text']
                    for status in statuses
                        for hashtag in status['entities']['hashtags']]
    urls = [url['expanded_url']
                for status in statuses
                    for url in status['entities']['urls'] ]
    symbols = [symbol['text']
                    for status in statuses
                        for symbol in status['entities']['symbols']]
    # In some circumstances (such as search results), the media entity
    # may not appear
    if status['entities'].has_key('media'):
        media = [media['url']
                    for status in statuses
                        for media in status['entities']['media']]
    else:
        media = []
    return screen_names, hashtags, urls, media, symbols





def get_common_tweet_entities(statuses, entity_threshold=3):
    # Create a flat list of all tweet entities
    tweet_entities = [ e
                        for status in statuses
                            for entity_type in extract_tweet_entities([status])
                                for e in entity_type
                    ]
    c = Counter(tweet_entities).most_common()
    # Compute frequencies
    return [ (k,v)
            for (k,v) in c
                if v >= entity_threshold
            ]


def print_prettytable(common_entities):
    pt = PrettyTable(field_names=['Entity', 'Count'])
    [ pt.add_row(kv) for kv in common_entities ]
    pt.align['Entity'], pt.align['Count'] = 'l', 'r' # Set column alignment
    print pt

