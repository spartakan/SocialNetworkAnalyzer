import datetime,json,time
import pymongo
import datetime
import sys,platform,os
if platform.system() == 'Linux':
    sys.path.insert(0,os.path.abspath("/home/sd/twitterAnalyzer"))
from debugging_setup import setup_logging, debug_print
from pymongo.errors import DuplicateKeyError
import logging
logger = logging.getLogger(__name__)
logger = setup_logging(logger)


def save_to_mongo(data, mongo_db, mongo_db_coll, **mongo_conn_kw):
    """
    Saves only one tweet at a time. The iteration part should be implemented in the method calling
    this one
    :parameter data should contain json file with only one tweet
    """
    #debug_print("Saving to database: exec save_to_mongo() method ...")
    # Connects to the MongoDB server running on
    # localhost:27017 by default
    client = pymongo.MongoClient(**mongo_conn_kw)

    # Get a reference to a particular database
    db = client[mongo_db]

    # Reference a particular collection in the database
    coll = db[mongo_db_coll]
    #oll.create_index("recent_retweets")
    try:
        coll.ensure_index([("id", 1)], unique=True)
        coll.ensure_index("hashtags.text")

        date = data['created_at']
        date = datetime.datetime.strptime(date, '%a %b %d %H:%M:%S +0000 %Y')
        #debug_print("DATE : " + str(date))
        data["DATE"] = unicode(date)
        #debug_print(json.dumps(d, indent=1))
        #break
        coll.ensure_index("DATE")
    except (Exception, DuplicateKeyError), e:
        debug_print(e)
        logger.error(e)
        pass
    try:
        status = coll.insert(data)
    except (Exception, DuplicateKeyError), e:
        debug_print(e)
        logger.error(e)
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
    :param find_since_id determines whether to return just the highest since_id from the collection or whether all documents should be returned
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