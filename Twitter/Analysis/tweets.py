
from collections import Counter
from prettytable import PrettyTable

from config import *

from DatabaseModule.database_manipulation import load_from_mongo

#create a logger for this module , set it up, and use it to write errors to file
logger = logging.getLogger(__name__)
logger = setup_logging(logger)
#sorting order
DESC =- 1
ASC = 1

def extract_tweet_entities(statuses):
    """ Extracts all entities from a list of given statuses.
    :parameter: statuses  - list of statuses from which the entities should be extracted
    :returns:  screen_names, hashtags, urls, media, symbols - lists of entities
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


def get_popular_tweet_entities_list(statuses=None, entity_threshold=3):
    """ Returns lists of most popular entities whose appearance exceeds the threshold.
    :parameter: statuses - list of statuses from which the entities should be extracted
    :parameter: entity_entity_threshold - the smallest number of appearances that needs to be excited for a status to be considered popular
    :returns: screen_names, hashtags, urls, media, symbols - dictionaries where the entity is a key and the number of appearances is a value
    """
    debug_print("EXEC get_common_tweet_entities method :")
    screen_names, hashtags, urls, media, symbols = [],[],[],[],[]
    if statuses: # find most popular hashtags in a given list

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
    #via mongo using map reduce

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
    :parameter: statuses - list of statuses from which the entities should be extracted
    :parameter: entity_entity_threshold - the smallest number of appearances that needs to be excited for a status to be considered popular
    :returns: (k,v) - dictionary where the entity is a key and the number of appearances is a value
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
    :parameter: statuses - list of statuses
    :parameter: retweet_threshold - least amount of retweets
    """
    debug_print("EXEC find_popular_tweets method :")
    #sort the statuses in DESCENDING order
    statuses = sort_tweets(statuses)
    print '{0:10}  {1:10}   {2:20}   {3:20} '.format("Retweets", "Favorites", "User", "Tweet")
    for status in statuses:
        if status['retweet_count'] > retweet_threshold:
            text = status['text']
            text = text.encode('latin-1', 'ignore')  # for special characters that may occur
            print '{0:10d}  {1:10d}   {2:20}   {3:20} '.format(status['retweet_count'], status['favorite_count'], status['user']['name'], text)



def sort_tweets(statuses, order=DESC):
    """ Sorts the list of statuses first by number of retweets then by number of favorites
    :parameter: statuses - list of statuses to sort
    :parameter: order - order in which the list should be sorted. values: ASC and DESC
    :returns: statuses - sorted ist of statuses
    """
    debug_print("EXEC sort_tweets method :")

    # sort statuses by retweets, then by favourites
    if order == DESC:
        for i in range(0, len(statuses)):
            for j in range(i, len(statuses)):
                if statuses[i]['retweet_count'] < statuses[j]['retweet_count']:
                    statuses[i], statuses[j] = statuses[j], statuses[i]
                elif statuses[i]['retweet_count'] == statuses[j]['retweet_count']:
                    if statuses[i]['favorite_count'] < statuses[j]['favorite_count']:
                        statuses[i], statuses[j] = statuses[j], statuses[i]
    elif order == ASC:
         for i in range(0, len(statuses)):
            for j in range(i, len(statuses)):
                if statuses[i]['retweet_count'] > statuses[j]['retweet_count']:
                    statuses[i], statuses[j] = statuses[j], statuses[i]
                elif statuses[i]['retweet_count'] == statuses[j]['retweet_count']:
                    if statuses[i]['favorite_count'] > statuses[j]['favorite_count']:
                        statuses[i], statuses[j] = statuses[j], statuses[i]
    return statuses

def get_popular_hashtags(slug):
    """
    Returns popular hastags for a certain list of users
    :parameter: slug - slug for the list from twitter
    :returns: hashtags - dictionary where key is the hashtag and value number of occurrences
    """
    debug_print("EXEC get_popular_hashtags method :")
    mongo_db = "twitter"
    mongo_db_coll = slug
    results = load_from_mongo(mongo_db=mongo_db, mongo_db_coll=mongo_db_coll)
    screen_names, hashtags, urls, media, symbols = get_popular_tweet_entities_list(results,25)
    #hashtags = get_popular_tweet_entities_list(entity_threshold= 25)
    hashtags_dict = {}
    for (k, v) in hashtags:
        print k, " : ", v
        hashtags_dict.update({k: v})
    return hashtags_dict


def get_users_for_hashtag_list(hashtags):
    """
    Counts the number of users that used the hashtags from the list in their posts
    :param hashtags - list of hashtags
    :return: users_per_hashtag - dict where key the hastag and value number of users that have included it in their posts
    """
    debug_print("EXEC get_users_for_hashtag_list method :")
    users_per_hashtag = {}

    for hashtag in hashtags:
        criteria = {"entities.hashtags.text": "%s" % hashtag}
        projection = {"user.screen_name": 1, "_id": 0}
        results = load_from_mongo(mongo_db="twitter", mongo_db_coll="community-councils",
                                  criteria=criteria, projection=projection)

        unique_users = set()
        for user in results:
            #print user["user"]["screen_name"]
            unique_users.add(user["user"]["screen_name"])
        #print hashtag
        #print len(unique_users)
        users_per_hashtag.update({hashtag:unique_users})
    return users_per_hashtag


def twitter_get_hashtags_from_tweets(tweets):
    """ Get hashtags used in a list of tweets
    :parameter: tweets:  list
    :return: hashtags - set of unique hashtags used in the tweets list
    """
    screen_names, hashtags, urls, media, symbols = extract_tweet_entities(tweets)
    #remove duplicates
    hashtags = set(hashtags)
    return hashtags

