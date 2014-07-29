import logging, os, sys, platform, re
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from collections import Counter
from prettytable import PrettyTable
from debugging_setup import setup_logging, debug_print
import logging
logger = logging.getLogger(__name__)
logger = setup_logging(logger)
import  collections

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
    return [(k, v)
            for(k, v) in c
                if v >= entity_threshold
            ]


def print_prettytable(common_entities):
    pt = PrettyTable(field_names=['Entity', 'Count'])
    [ pt.add_row(kv) for kv in common_entities ]
    pt.align['Entity'], pt.align['Count'] = 'l', 'r' # Set column alignment
    print pt


def find_popular_tweets(twitter_api, statuses, retweet_threshold=3):

    # You could also consider using the favorite_count parameter as part of
    # this  heuristic, possibly using it to provide an additional boost to
    # popular tweets in a ranked formulation

    # return [ status
    #             for status in statuses
    #                 if status['retweet_count'] > retweet_threshold ]

    print '{0:10}  {1:10}   {2:20}   {3:20} '.format("Retweets", "Favorites", "User", "Tweet")
    statuses = sort_statuses(statuses)
    for status in statuses:
        if status['retweet_count'] > retweet_threshold:
            text = status['text']
            text = text.encode('latin-1', 'ignore')
            print '{0:10d}  {1:10d}   {2:20}   {3:20} '.format(status['retweet_count'], status['favorite_count'], status['user']['name'], text)


def sort_statuses(statuses):
    # sort statuses by retweets, then by favourites
    for i in range(0, len(statuses)):
        for j in range(i, len(statuses)):
            if statuses[i]['retweet_count'] < statuses[j]['retweet_count']:
                statuses[i], statuses[j] = statuses[j], statuses[i]
            elif statuses[i]['retweet_count'] == statuses[j]['retweet_count']:
                if statuses[i]['favorite_count'] < statuses[j]['favorite_count']:
                    statuses[i], statuses[j] = statuses[j], statuses[i]
    return statuses