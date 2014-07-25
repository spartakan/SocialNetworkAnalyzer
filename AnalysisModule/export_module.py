import sys, os, platform
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from debugging_setup import  debug_print
import networkx as nx


#get tweets from database
criteria = {"retweet_count":{"$gt":400}}
projection = {"_id": 1, "retweet_count": 1, "favorite_count":1}
tweets = load_from_mongo("twitter","#indyref",criteria=criteria,projection=projection)
debug_print("Printing fetched data in export_module ...")
debug_print([tweet for tweet in tweets])


G=nx.Graph()
#add all the tweets as nodes with weight determined from the number of retweets and favourites
for tweet in tweets:
    weight = tweet['retweet_count'] * 0.6
    weight = weight + tweet['favorite_count']* 0.4
    # G.add_node(name_of_node, attr1 = attr1, attr2= attr2 ...)
    G.add_node(tweet['_id'], retweet_count=tweet['retweet_count'], weight = weight)
print G.nodes(data=True)
print(G.number_of_nodes())
#nx.write_gml(G,"c:/mongodb/test.gml")