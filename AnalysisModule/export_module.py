import sys, os, platform
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from debugging_setup import  debug_print
import networkx as nx

G=nx.Graph()
criteria = {"retweet_count":{"$gt":700}}
projection = {"_id": 1, "retweet_count": 1}
tweets = load_from_mongo("twitter","#indyref",criteria=criteria,projection=projection)
debug_print("Printing fetched data in export_module ...")
debug_print([tweet for tweet in tweets])
for tweet in tweets:
    G.add_node(id=tweet['_id'], retweet_count=tweet['retweet_count'])
print G.nodes(data=True)