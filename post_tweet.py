import os, time
from twitter_bot_class import TwitterBot
import configparser



if __name__ == "__main__":
    config = configparser.ConfigParser(allow_no_value=True)
    config.read('config.conf')

    email = config.get('account', 'email')
    password = config.get('account', 'password')
    userName = config.get('account', 'userName')
    searchKeys = config.get('search', 'searchKeys')
    userIdsPath = config.get('output', 'outputPath')
    maxScrollDownTimes = config.get('settings', 'maxScrollDownTimes')

    userId = config.get('search', 'userId')

    tb = TwitterBot(email, password, userName, maxScrollDownTimes)
    tb.loginAbnormal()
    time.sleep(5)
    # result = tb.searchLikesUsers(userId, userIdsPath)
    tb.searchForLikesUsersTweetsAndLocation(userIdsPath)



