from DatabaseModule.TwitterWrapper.database_manipulation import twitter_load_from_mongo_sorted, twitter_save_to_mongo


def twitter_date_of_last_tweet(screen_name):
    """

    :param screen_name:
    :return: date of last tweet
    """

    result = twitter_load_from_mongo_sorted(screen_name, 1)
    last_tweet = result[0]
    return last_tweet["DATE"]


def twitter_date_of_fifth_tweet(screen_name):
    """

    :param screen_name:
    :return: date of the fifth tweet sorted in DESC order
    """
    result = twitter_load_from_mongo_sorted(screen_name, 5)
    idx = len(result)-1
    fifth_tweet = result[idx]
    return fifth_tweet["created_at"]

