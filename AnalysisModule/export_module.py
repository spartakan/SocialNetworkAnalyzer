import sys, os, platform
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from DatabaseModule.database_manipulation import save_to_mongo, load_from_mongo
from debugging_setup import  debug_print
from debugging_setup import setup_logging, debug_print
import logging
logger = logging.getLogger(__name__)
logger = setup_logging(logger)

import networkx as nx

def create_keyplayers_graph(graph, user, followers):
    debug_print("EXEC - create_keyplayers_graph method :")

    #add the user who is followed as a node
    graph.add_node(user['id'], screen_name=user['screen_name'], location=user['location'],
                   followers_count=user['followers_count'], statuses_count=user['followers_count'],
                   friends_count=user['friends_count'], created_at=user['created_at'])

    #add the followers as nodes
    for follower in followers:
        graph.add_node(follower['id'], screen_name=follower['screen_name'], location=follower['location'],
                   followers_count=follower['followers_count'], statuses_count=follower['followers_count'],
                   friends_count=follower['friends_count'], created_at=follower['created_at'])

    #debug_print("nodes : " + graph.nodes())
    debug_print("  num of nodes: "+str(graph.number_of_nodes()))

    #add edges from the followers to the one who is followed
    for follower in followers:
        graph.add_edge(follower['id'], user['id'])

    #debug_print("edges : " + graph.edges())
    debug_print("  num of edges: " + str(graph.number_of_edges()))
    return graph


def export_graph_to_gml(graph,path):
    debug_print("EXEC - export_graph_to_gml method :")
    nx.write_gml(graph, path)


def import_graph_from_gml(path):
    debug_print("EXEC - import_graph_from_gml method :")
    graph = None
    try:
        graph = nx.read_gml(path)
    except Exception, e:
        debug_print("  Exception: %s" % e)
    return  graph