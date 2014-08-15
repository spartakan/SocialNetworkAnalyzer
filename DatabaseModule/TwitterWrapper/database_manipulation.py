from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo,load_from_mongo_sorted
from debugging_setup import  *
import datetime
import pymongo
from config import *
from pymongo.errors import DuplicateKeyError
import logging
logger = logging.getLogger(__name__)
logger = setup_logging(logger)
DESC = -1
ASC = 1

def twitter_save_to_mongo(data, mongo_db, mongo_db_coll, indexes=None, **mongo_conn_kw):
    """
    Saves only one entity at a time. The iteration part should be implemented in the method calling
    this one
    :parameter data should contain json file with only one object/entity
    :parameter mongo_db contains the name of the database
    :parameter mongo_db_coll contains the name of the collection
    :parameter indexes contains a list of all the indexes you want to ensure besides the default: id=id; DATE=created_at;
    """
    debug_print("EXEC twitter_save_to_mongo method :")
    client = pymongo.MongoClient(**mongo_conn_kw)

    # Get a reference to a particular database
    db = client[mongo_db]

    # Reference a particular collection in the database
    coll = db[mongo_db_coll]
    #oll.create_index("recent_retweets")
    for document in data:
        try:
            coll.ensure_index([("id", 1)], unique=True)
            date = document['created_at']
            date = datetime.datetime.strptime(date, '%a %b %d %H:%M:%S +0000 %Y')
            #debug_print("DATE : " + str(date))
            document["DATE"] = unicode(date)
            #debug_print(json.dumps(d, indent=1))
            #break
            coll.ensure_index("DATE")
            #ensure all other indexes
            if indexes is not None:
                for idx in indexes:
                    coll.ensure_index([(idx, 1)])
            status = coll.insert(document)

        except (Exception, DuplicateKeyError), e:
            debug_print("  Exception: %s" % e.message)
            logger.error(e)
            pass


def twitter_load_from_mongo_sorted(screen_name, limit=None):
    """
    Returns all tweets
    :param screen_name:
    :return:
    """
    sort_params = [("DATE", DESC)]
    return load_from_mongo_sorted(mongo_db="twitter", mongo_db_coll=screen_name, limit=limit, sort_params=sort_params)

