import sys, os, platform
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from debugging_setup import  debug_print
import networkx as nx


def create_graph(G):
    debug_print("EXEC - create_graph method :")
    #get tweets from database
    criteria = {"retweet_count": {"$gt": 400}}
    projection = {"_id": 1, "retweet_count": 1, "favorite_count":1}
    tweets = load_from_mongo("twitter","#indyref",criteria=criteria,projection=projection)
    debug_print("Printing fetched data in export_module ...")
    debug_print([tweet for tweet in tweets])
    #add all the tweets as nodes with weight determined from the number of retweets and favourites
    for tweet in tweets:
        weight = tweet['retweet_count'] * 0.6
        weight = weight + tweet['favorite_count']* 0.4
        # G.add_node(name_of_node, attr1 = attr1, attr2= attr2 ...)
        G.add_node(tweet['_id'], retweet_count=tweet['retweet_count'], weight = weight)
    print G.nodes(data=True)
    print(G.number_of_nodes())
    #nx.write_gml(G,"c:/mongodb/test.gml")


def create_keyplayers_graph(graph, user, followers):
    debug_print("EXEC - create_keyplayers_graph method :")
    #add the main user
    graph.add_node(user['id'], screen_name=user['screen_name'])
    for follower in followers:
        graph.add_node(follower['id'], screen_name=follower['screen_name'])
    print "nodes:"
    print graph.nodes()
    print("num of nodes: "+str(graph.number_of_nodes()))

    #add edges
    for follower in followers:
        #directed from follower -> to user
        graph.add_edge(follower['id'], user['id'])
    print graph.edges()
    print "num of edges: ", graph.number_of_edges()
    return graph


def export_graph_to_gml(graph):
    nx.write_gml(graph, "c:/data/graph_followers2.gml")