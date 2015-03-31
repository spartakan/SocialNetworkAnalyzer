from DatabaseModule.database_manipulation import save_to_mongo,load_from_mongo
from debugging_setup import  *
import datetime
import pymongo
from config import *
from pymongo.errors import DuplicateKeyError
import logging
logger = logging.getLogger(__name__)
logger = setup_logging(logger)

#Functions that will define logic and indexes for the data saved in collections

