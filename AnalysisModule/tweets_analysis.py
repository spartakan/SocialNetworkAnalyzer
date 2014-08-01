import logging, os, sys, platform, re
from DatabaseModule.database_manipulation import load_from_mongo,load_from_mongo_with_mapreduce
from bson.code import Code
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from collections import Counter
from prettytable import PrettyTable
from debugging_setup import setup_logging, debug_print

#create a logger for this module , set it up, and use it to write errors to file
logger = logging.getLogger(__name__)
logger = setup_logging(logger)


def extract_tweet_entities(statuses):
    """ Extracts all entities from a list of given statuses.
    :parameter statuses  - list of statuses from which the entities should be extracted
    :returns screen_names, hashtags, urls, media, symbols - lists of entities
    """
    debug_print("EXEC extract_tweet_entities method :")

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
                for url in status['entities']['urls']]
    symbols = [symbol['text']
                    for status in statuses
                        for symbol in status['entities']['symbols']]

    # In some circumstances (such as search results), the media entity
    # may not appear
    media = []
    for status in statuses:
        if 'media' in status['entities']:
            media = media + [media['url']
                             for media in status['entities']['media']]

    return screen_names, hashtags, urls, media, symbols


def get_listsof_popular_tweet_entities(statuses = None, entity_threshold=3):
    """ Returns lists of most popular entities whose appearance exceeds the threshold.
    :parameter statuses - list of statuses from which the entities should be extracted
    :parameter entity_entity_threshold - the smallest number of appearances that needs to be excited for a status to be considered popular
    :returns screen_names, hashtags, urls, media, symbols - dictionaries where the entity is a key and the number of appearances is a value
    """
    debug_print("EXEC get_common_tweet_entities method :")
    screen_names, hashtags, urls, media, symbols = [],[],[],[],[]
    if statuses: # find most popular hashtags ina given list

        screen_names, hashtags, urls, media, symbols = extract_tweet_entities(statuses)
        screen_names_counter = Counter(screen_names).most_common()
        hashtags_counter = Counter(hashtags).most_common()
        urls_counter = Counter(urls).most_common()
        media_counter = Counter(media).most_common()
        symbols_counter = Counter(symbols).most_common()

        screen_names = [(k, v)
                        for(k, v) in screen_names_counter
                        if v >= entity_threshold]
        hashtags = [(k, v)
                    for(k, v) in hashtags_counter
                    if v >= entity_threshold]
        urls = [(k, v)
                for(k, v) in urls_counter
                if v >= entity_threshold]
        media = [(k, v)
                 for(k, v) in media_counter
                 if v >= entity_threshold]
        symbols = [(k, v)
                   for(k, v) in symbols_counter
                   if v >= entity_threshold]

    return screen_names, hashtags, urls, media, symbols


    #To create different map - reduce functions check: http://api.mongodb.org/python/2.0/examples/map_reduce.html
    # and http://cookbook.mongodb.org/patterns/count_tags/

    #count the number of occurrences for each hashtag in the hashtags array, across the entire collection
    #via mongo

    # map = Code(" function() {"
    #            "if (!this.entities.hashtags) {"
    #            "  return;"
    #            " }"
    #            " for (index in this.entities.hashtags) {"
    #            "    emit(this.entities.hashtags[index].text, 1);"
    #            "}"
    #            "}")
    # #sum over all of the emitted values for a given key
    # reduce = Code("function(previous, current) {"
    #               "var count = 0;"
    #               "for (index in current) {"
    #               " count += current[index];"
    #               " }"
    #               " return count;"
    #               "}")
    #
    #
    # hashtags = load_from_mongo_with_mapreduce(mongo_db="twitter", mongo_db_coll="community-councils", map=map, reduce=reduce, newDatabase="popularHashtags")
    # #print hashtags




def get_common_tweet_entities(statuses, entity_threshold=3):
    """ Returns a list most common entities in a list of statuses whose appearance exceeds the threshold.
    :parameter statuses - list of statuses from which the entities should be extracted
    :parameter entity_entity_threshold - the smallest number of appearances that needs to be excited for a status to be considered popular
    :returns (k,v) - dictionary where the entity is a key and the number of appearances is a value
    """
    debug_print("EXEC get_common_tweet_entities method :")
    # Create a flat list of all tweet entities
    tweet_entities = [e
                        for status in statuses
                            for entity_type in extract_tweet_entities([status])
                                for e in entity_type]
    print  tweet_entities
    c = Counter(tweet_entities).most_common()
    #sorted(c.items(), key=c.items(), reverse=True)
    # Compute frequencies and return dictionary
    return [(k, v)
            for(k, v) in c
                if v >= entity_threshold]
            #sorted(c.items(), key=c.items(), reverse=True)



def print_prettytable(common_entities):
    """ Tabulates the results of frequency analysis experiments in order to easily skim the results.
    :parameter common_entities - dictionary of entities and frequencies to display
    """
    debug_print("EXEC print_prettytable method :")

    #add columns' names
    pt = PrettyTable(field_names=['Entity', 'Count'])
    [pt.add_row(kv) for kv in common_entities]   # add rows
    pt.align['Entity'], pt.align['Count'] = 'l', 'r'  # Set column alignment
    print pt


def find_popular_tweets(statuses, retweet_threshold=3):
    """ Displays popular statuses that exceed the given threshold for retweets
    :parameter statuses - list of statuses
    :parameter retweet_threshold - least amount of retweets
    """
    debug_print("EXEC find_popular_tweets method :")
    #sort the statuses in DESCENDING order
    statuses = sort_statuses(statuses)
    print '{0:10}  {1:10}   {2:20}   {3:20} '.format("Retweets", "Favorites", "User", "Tweet")
    for status in statuses:
        if status['retweet_count'] > retweet_threshold:
            text = status['text']
            text = text.encode('latin-1', 'ignore')  # for special characters that may occur
            print '{0:10d}  {1:10d}   {2:20}   {3:20} '.format(status['retweet_count'], status['favorite_count'], status['user']['name'], text)



def sort_statuses(statuses, order="DESC"):
    """ Sorts the list of statuses first by number of retweets then by number of favorites
    :parameter statuses - list of statuses to sort
    :parameter order - order in which the list should be sorted. values: ASC and DESC
    :returns statuses - sorted ist of statuses
    """
    debug_print("EXEC sort_statuses method :")

    # sort statuses by retweets, then by favourites
    if order == "DESC":
        for i in range(0, len(statuses)):
            for j in range(i, len(statuses)):
                if statuses[i]['retweet_count'] < statuses[j]['retweet_count']:
                    statuses[i], statuses[j] = statuses[j], statuses[i]
                elif statuses[i]['retweet_count'] == statuses[j]['retweet_count']:
                    if statuses[i]['favorite_count'] < statuses[j]['favorite_count']:
                        statuses[i], statuses[j] = statuses[j], statuses[i]
    elif order == "ASC":
         for i in range(0, len(statuses)):
            for j in range(i, len(statuses)):
                if statuses[i]['retweet_count'] > statuses[j]['retweet_count']:
                    statuses[i], statuses[j] = statuses[j], statuses[i]
                elif statuses[i]['retweet_count'] == statuses[j]['retweet_count']:
                    if statuses[i]['favorite_count'] > statuses[j]['favorite_count']:
                        statuses[i], statuses[j] = statuses[j], statuses[i]
    return statuses