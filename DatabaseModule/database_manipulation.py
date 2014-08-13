import pymongo
from config import *
from pymongo.errors import DuplicateKeyError
import logging
logger = logging.getLogger(__name__)
logger = setup_logging(logger)


def save_to_mongo(data, mongo_db, mongo_db_coll, coll=None, **mongo_conn_kw):
    """
    Saves only one entity at a time. The iteration part should be implemented in the method calling
    this one
    :parameter data should contain json file with only one object/entity
    :parameter mongo_db contains the name of the database
    :parameter mongo_db_coll contains the name of the collection
    :parameter indexes contains a list of all the indexes you want to ensure besides the default: id=id; DATE=created_at;
    """
    debug_print("EXEC save_to_mongo method :")

    # Connects to the MongoDB server running on
    # localhost:27017 by default

    if coll is None:
        client = pymongo.MongoClient(**mongo_conn_kw)

        # Get a reference to a particular database
        db = client[mongo_db]

        # Reference a particular collection in the database
        coll = db[mongo_db_coll]

    try:
        coll.ensure_index([("id", 1)], unique=True)
        status = coll.insert(data)

    except (Exception, DuplicateKeyError), e:
        debug_print("  Exception: %s" % e.message)
        logger.error(e)
        pass



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
    debug_print("EXEC load_from_mongo method :")
    # Optionally, use criteria and projection to limit the data that is
    # returned as documented in
    # http://docs.mongodb.org/manual/reference/method/db.collection.find/

    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]
    if find_since_id:
        result = coll.find_one({"$query": {}, "$orderby": {"id": -1}}, {"id": 1})
       # print result[u'id']
        if result:
            return result[u'id']
        else:
            return None
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


def load_from_mongo_with_mapreduce(mongo_db, mongo_db_coll, map,reduce, newDatabase="default_map_reduce", limit=5, order=pymongo.DESCENDING, **mongo_conn_kw):
    """
    Loads data from the specific database and the specific collection by the chosen criteria
    :param mongo_db
    :param mongo_db_coll
    :param map
    :param reduce
    :param limit
    :parameterorder
    :param mongo_conn_kw

    """
    debug_print("EXEC load_from_mongo method :")
    # Optionally, use criteria and projection to limit the data that is
    # returned as documented in
    # http://docs.mongodb.org/manual/reference/method/db.collection.find/

    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]
    result = coll.map_reduce(map, reduce,newDatabase)
    #for r in result.find().sort("value", order).limit(limit):
        #print r

    return result.find().sort("value", order).limit(limit)

def load_from_mongo_sorted(mongo_db, mongo_db_coll, return_cursor=False, criteria=None, projection=None, sort_params=None, limit=5, **mongo_conn_kw):
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
    debug_print("EXEC load_from_mongo_sorted method :")
    # Optionally, use criteria and projection to limit the data that is
    # returned as documented in
    # http://docs.mongodb.org/manual/reference/method/db.collection.find/

    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]

    if criteria is None:  # set criteria
        criteria = {}

    if criteria is not None and projection is not None and sort_params is not None:
        cursor = coll.find(criteria, projection).sort(sort_params)
        debug_print("  All criteria set")
    elif projection is None:
        debug_print("  No projection")
        cursor = coll.find(criteria).sort(sort_params).limit(limit)
    else:
        cursor = coll.find(criteria)
        debug_print("  Not sorted")

        # Returning a cursor is recommended for large amounts of data
    if return_cursor:
        return cursor
    else:
        return [item for item in cursor]