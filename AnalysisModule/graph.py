import sys, os, platform, logging
if platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath("/home/sd/twitterAnalyzer"))
from debugging_setup import setup_logging, debug_print
import networkx as nx

#create a logger for this module , set it up, and use it to write errors to file
logger = logging.getLogger(__name__)
logger = setup_logging(logger)


def create_keyplayers_graph(graph, user, followers):
    """Creates nodes which represent the users' with attributes : screen_name, location, followers_count,
                                                                 statuses_count, friends_count, created_at
       and edges from the followers to the user.
       :parameter graph - an instance of networkx graph
       :parameter user - the node that the other nodes point at
       :parameter followers - the nodes who are pointing
       :returns graph - with nodes and edges between them

    """
    debug_print("EXEC - create_keyplayers_graph method :")

    #add as a node the user who is followed
    graph.add_node(user['id'], screen_name=user['screen_name'], location=user['location'],
                   followers_count=user['followers_count'], statuses_count=user['statuses_count'],
                   friends_count=user['friends_count'], created_at=user['created_at'])

    #add the followers as nodes
    for follower in followers:
        graph.add_node(follower['id'], screen_name=follower['screen_name'], location=follower['location'],
                       followers_count=follower['followers_count'], statuses_count=follower['followers_count'],
                       friends_count=follower['friends_count'], created_at=follower['created_at'])

    debug_print("  num of nodes: "+str(graph.number_of_nodes()))

    #add edges from the followers to the one who is followed
    for follower in followers:
        graph.add_edge(follower['id'], user['id'])

    debug_print("  num of edges: " + str(graph.number_of_edges()))
    return graph


def export_graph_to_gml(graph, path):
    """ Exports a given graph to a gml format and saves it on the given path.
    :parameter graph - graph to be exported
    :parameter path - where to save the .gml file
    """
    debug_print("EXEC - export_graph_to_gml method :")
    nx.write_gml(graph, path)


def import_graph_from_gml(path):
    """ Imports a graph saved as a gml file from the given path and returns a networkx object.
    :parameter path - where to find the .gml file
    :returns graph - imported graph
    """
    debug_print("EXEC - import_graph_from_gml method :")
    graph = None
    try:
        graph = nx.read_gml(path)
    except Exception, e:
        debug_print("  Exception: %s" % e)
    return  graph