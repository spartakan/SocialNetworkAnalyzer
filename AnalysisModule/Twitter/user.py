from DatabaseModule.TwitterWrapper.database_manipulation import twitter_load_from_mongo_sorted


def twitter_date_of_last_tweet(owner_screen_name,slug):
    """
     Get the date of the last tweet for a screen_name, from database

    :parameter: screen_name:
    :return: date of last tweet
    """

    result = twitter_load_from_mongo_sorted(mongo_db="twitter",mongo_db_coll=slug,criteria={"user.screen_name":owner_screen_name}, limit=1)
    if result:
        last_tweet = result[0]
        return last_tweet["DATE"]
    else:
        return 0


def twitter_date_of_fifth_tweet(owner_screen_name,slug):
    """
    Get the date of the fifth tweet for a given screen_name.
    If less than five tweets are posted then returns the last.

    :parameter: screen_name:
    :return: date of the fifth tweet sorted in DESC order
    """
    result = twitter_load_from_mongo_sorted(mongo_db="twitter",mongo_db_coll=slug,criteria={"user.screen_name":owner_screen_name}, limit=5)
    idx = len(result)-1
    if len(result) > 0: #check if there are any posts in database for this screen_name
        fifth_tweet = result[idx]
        return fifth_tweet["DATE"]
    else:  # no tweets saved in database
        return 0

