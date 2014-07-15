import logging
import os
import platform
import sys
import pymongo
import datetime
import json
import sys



#to print info messages debug must be true!
debug = True
logger = logging.getLogger(__name__)

def debug_print(message):
    """
    Prints messages if the debug variable is set to true
    :param message: message to be printed
    :return: none
    """""
    if debug:
        print >> sys.stderr, "INFO: ", message
        print >> sys.stderr.flush()

def setup_logging():
    """
    Initializing the logging system used to write errors to a log file
    """
   #ceating a file handler
    #logger.level(logging.INFO)
    if platform.system() == 'Windows':
        LOG_FILE = os.path.expanduser("C:/Users/Windows/Desktop/twitterAnalyzer/CrawlingModule/Resources/error.log").replace("\\", "/")
    elif platform.system() == 'Linux':
        LOG_FILE = os.path.abspath(os.path.expanduser("~/twitterAnalyzer/CrawlingModule/Resources/error.log"))
    handler = logging.FileHandler(LOG_FILE)
    handler.setLevel(logging.ERROR)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)


#setup the logger with proper handler
setup_logging()


def save_to_mongo(data, mongo_db, mongo_db_coll, **mongo_conn_kw):
    """
    Storing nontrivial amounts of JSON data from Twitter API with indexing included.
    """
    debug_print("Executing save_to_mongo() method ...")
    # Connects to the MongoDB server running on
    # localhost:27017 by default
    client = pymongo.MongoClient(**mongo_conn_kw)

    # Get a reference to a particular database
    db = client[mongo_db]

    # Reference a particular collection in the database
    coll = db[mongo_db_coll]
    #oll.create_index("recent_retweets")
    coll.ensure_index([("id",1)],unique=True)
    coll.ensure_index("hashtags.text")
    for d in data:
        #debug_print(json.dumps(d, d, indent=1))
        date = d[u'created_at']
        date = datetime.datetime.strptime(date, '%a %b %d %H:%M:%S +0000 %Y')
        #debug_print("DATE : " + str(date))
        d["DATE"] = unicode(date)
        #debug_print(json.dumps(d, indent=1))
        break
    coll.ensure_index("DATE")
    try:
        status = coll.insert(data)
    except Exception,e :
        pass
    else:
        return status



def load_from_mongo(mongo_db, mongo_db_coll, return_cursor=False, criteria=None, projection=None, find_since_id=False, **mongo_conn_kw):
    """
    Loads data from the specific database and the specific collection by the chosen criteria
    :param mongo_db
    :param mongo_db_coll
    :param return_cursor
    :param criteria
    :param projection
    :param mongo_conn_kw
    """
    # Optionally, use criteria and projection to limit the data that is
    # returned as documented in
    # http://docs.mongodb.org/manual/reference/method/db.collection.find/

    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]
    if find_since_id:
        result = coll.find_one({"$query": {}, "$orderby": {"id": -1}}, {"id": 1})
       # print result[u'id']
        return result[u'id']

    else:
        if criteria is None:
            criteria = {}
        if projection is None:
            cursor = coll.find(criteria)
        else:
            cursor = coll.find(criteria, projection)
            # Returning a cursor is recommended for large amounts of data
        if return_cursor:
            return cursor
        else:
            return [item for item in cursor]