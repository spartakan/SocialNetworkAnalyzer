from DatabaseModule.database_manipulation import load_from_mongo
import networkx as nx
from config import *
from CrawlingModule.Twitter.user import twitter_get_followers
#create a logger for this module , set it up, and use it to write errors to file
logger = logging.getLogger(__name__)
logger = setup_logging(logger)


def create_keyplayers_graph(graph, user, followers, weight):
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
        graph.add_edge(follower['id'], user['id'], weight=weight)

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

def create_directed_graph_of_list_members(list):
    """Creates a directed graph where nodes are all members of a given list and edges are
     added if a member has replied to another one on twitter
     :parameter list
     :return dG - directed graph
     """
    debug_print("EXEC - create_directed_graph_of_list_members method :")

    criteria = {"in_reply_to_user_id": {"$ne": None}, "$where": "this.user.id != this.in_reply_to_user_id"}
    projection = {"id": 1, "user.screen_name": 1, "in_reply_to_screen_name": 1, "in_reply_to_user_id": 1, "text": 1}
    # tweets that aren't a reply to the same user's tweets
    results = load_from_mongo(mongo_db="twitter", mongo_db_coll=list, criteria=criteria, projection=projection)

    debug_print("  num of edges/results: %d" % len(results))
    dG = nx.DiGraph()
    db_coll_name = "%s_%s" % (list, "members")
    members = load_from_mongo(mongo_db="twitter", mongo_db_coll=db_coll_name)
    debug_print("  num of members: %d" % len(members))
    for member in members:
        dG.add_node(member['id'], screen_name=member['screen_name'], location=member['location'],
           followers_count=member['followers_count'], statuses_count=member['followers_count'],
           friends_count=member['friends_count'], created_at=member['created_at'])
    i = 0
    for result in results:

        if dG.has_node(result['id']) and dG.has_node(result['in_reply_to_user_id']):
            debug_print("%d) user: %s \n          in reply to: %s \n          text: %s" % (i,result['user']['screen_name'],result['in_reply_to_screen_name'],result['text']))
            i += 1
            dG.add_edge(result['id'], result['in_reply_to_user_id'])
    return dG

def create_directed_graph_of_list_members_and_followers(api, list):
    """Creates a directed graph where nodes are all members of a given list and edges are
     added if a member who follows another one on twitter.
     :parameter api
     :parameter list
     :return dG - directed graph
     """
    debug_print("EXEC - create_directed_graph_of_list_members_and_followers method :")
    criteria = {"in_reply_to_user_id": {"$ne": None}, "$where": "this.user.id != this.in_reply_to_user_id"}
    projection = {"id": 1, "user.screen_name": 1, "in_reply_to_screen_name": 1, "in_reply_to_user_id": 1, "text": 1}
    tweets = load_from_mongo(mongo_db="twitter", mongo_db_coll=list, criteria=criteria, projection=projection)

    #create a multi directed graph - one directions for reply / one for following
    dG = nx.DiGraph()
    db_coll_name = "%s_%s" % (list, "members")
    members = load_from_mongo(mongo_db="twitter", mongo_db_coll=db_coll_name)
    for member in members:
        followers = twitter_get_followers(api, screen_name=member['screen_name'],followers_limit=400)
        #print member['screen_name'],len(followers)

        #create network of following
        dG = create_keyplayers_graph(graph=dG, user=member, followers=followers, weight=1)
    return dG


def create_multi_graph_of_list_memebers_and_followers(api, list):
    """Creates a multi directed graph where nodes are all members of a given list and their followers and edges(weight 1) are
    added if a user follows another one on twitter.
    Edges (weight 2) are added if one user replied to another one on twitter.
    :parameter api
    :parameter list
    :return mDG - multi directed graph
    """
    debug_print("EXEC - create_multi_graph_of_list_memebers_and_followers method :")

    criteria = {"in_reply_to_user_id": {"$ne": None}, "$where": "this.user.id != this.in_reply_to_user_id"}
    projection = {"id": 1, "user.screen_name": 1, "in_reply_to_screen_name": 1, "in_reply_to_user_id": 1, "text": 1}
    tweets = load_from_mongo(mongo_db="twitter", mongo_db_coll=list, criteria=criteria, projection=projection)

    #create a multi directed graph - one directions for reply / one for following
    mdG = nx.MultiDiGraph()
    db_coll_name = "%s_%s" % (list, "members")
    members = load_from_mongo(mongo_db="twitter", mongo_db_coll=db_coll_name)
    for member in members:   # for member in members[:10]: can be used for testing
        followers = twitter_get_followers(api, screen_name=member['screen_name'],followers_limit=400)
        print member['screen_name'],len(followers)
        #create network of following
        mdG = create_keyplayers_graph(graph=mdG, user=member, followers=followers, weight=1)

    #create network of conversation/replying
    i = 0
    for tweet in tweets:
        if mdG.has_node(tweet['id']) and mdG.has_node(tweet['in_reply_to_user_id']):
            debug_print("%d) user: %s \n          in reply to: %s \n          text: %s" % (i,tweet['user']['screen_name'],tweet['in_reply_to_screen_name'],tweet['text']))
            i += 1
            mdG.add_edge(tweet['id'], tweet['in_reply_to_user_id'],weight = 2)
    return mdG