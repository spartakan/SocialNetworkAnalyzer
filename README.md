

Technologies and guides
-----------------------



> This project is being led by O'Reilly's book,  Mining the Social Web.
> The programing language that is chosen for this project is Python, for
> its intuitive syntax, amazing ecosystem of packages that trivialize
> API access and data manipulation, and core data structures that are
> practically JSON, make it an excellent teaching tool that's powerful
> yet also very easy to get up and running.
> 


> VMware vSphere is used for providing virtualization on the server,
> because of advantages like performance monitoring and capacity
> management capabilities and robust security.
> 


> Libraries that are being used  : 
> 
> 
>  - twitter (used for making requests to the twitter api, preferred by O'Reilly)
>  - tweepy (used for authorization )

> 


> Storage : mongo database is chosen for its document-oriented storage(
> JSON-style documents) which will ease the manipulation with the data
> since twitter's responses are sent in json format.
> 


> The project is being developed in PyCharm 3.4 the free community
> edition because of the intelligent editor, the code completion,
> on-the-fly error highlighting, auto-fixes, etc.

Module Structure
----------------

The project is divided in two modules: 	Crawling Module and Analysis Module. The reason behind this decision is that the crawling and the analytical process are two independent processes and in order to have logically separated files that contain the logic of the corresponding processes they should be divided into two modules.
Crawling Module
The main purpose of this module is to collect all the data that we are interested in from twitter and save it into mongo database. The data should be saved in a way that will later ease the retrieval and analysing process. This module contains the following files:


----------


 -	\__init__.py
 -	main.py
 -	search_tweets.py
 -	authorization.py

__\__init__\__.py

In this file, the operating system on which the package is running is being determined and then according to it, the system path is set. 


----------


__main.py__

Methods:

 - setup_logging
 - main

This file contains the main order of the function calls from the other files. The call of a specific function is determined by the user through a simple menu. The first procedure that is called from the main function is the logging procedure. Firstly the error.log file where all the error logs are written, is located (in Resources folder) according to the operating system on which the script is running . The second procedure that is called from the main function is the one for authorization (from authorization.py function oauth_login).  After successful authorization the user can choose an action from the following ones: 

1.  Finding the trending topics in the world (from search_tweets.py function twitter_trends)

2.	Searching & saving trending topics on 15 seconds(from search_tweets.py function twitter_trends &save_time_series_data)

3.	Searching a limited number of tweets for a specific query  (from search_tweets.py function twitter_search)

4.	Searching & saving tweets for a specific query (from search_tweets.py function save_time_series_data & search_tweets)

5.	Searching & saving tweets from the streaming api (from search_tweets.py function save_tweets_form_stream_api)

6.	Loading tweets from the database for a specific query (from search_tweets.py function load_from_mongo)

7.	Getting tweets for specific user account (from search_tweets.py function harvest_user_timeline  & save_to_mongo)


----------


__authorization.py__

This script contains the *oauth_login function* which tries to authorize the applicaiton and obtain access key  and access secret from the twitter api. The consumer key and secret are acquired from twitter after the application has been registered on https://apps.twitter.com/app/new. When the authorization process is over, the access key and secret are written into a file so that with each following execution of the script, the user won't bothered again with authorization. This function returns an instance of the  'twitter.Api'  with login credentials, which is used in all other methods for sending requests.


----------


__search_tweets.py__

This file contains all the methods that involve interaction with twitter's api and mongo database. The methods are:

 

 - *setup_logging* is a method in which the logging system is being initialized to write all the errors to a log file.
   
 - *make_twitter_request*  is a nested helper function that handles common HTTPErrors. It is called inside all functions to make robust
   twitter requests .
 - *twitter_trends*  finds the top 10 trending topics for a specific WOEID.

  

 - *twitter_search*   retrieves tweets from the api for a given query.

   

 - *get_and_save_tweets_form_stream_api*  uses twitter's streaming api to
   get samples of the public data flowing through Twitter.

   
   

 - *save_to_mongo*  Stores nontrivial amounts of JSON data from Twitter
   API with indexing included.

  

 - *load_from_mongo*  Loads data from the specific database and the
   specific collection by the chosen criteria

   

 - *save_time_series_data*  Prevents reaching twitter's rest api rate
   limit and stores the results from the responses in the database

## Problems ##
TODO
