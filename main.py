import os, time
from twitter_bot_class import TwitterBot
import configparser
from utils import *



if __name__ == "__main__":
    config = configparser.ConfigParser(allow_no_value=True)
    config.read('config.conf')

    email = config.get('account', 'email')
    password = config.get('account', 'password')
    userName = config.get('account', 'userName')
    searchKeys = config.get('search', 'searchKeys')
    firstLevelUserTweetsFile = config.get('output', 'outputTweetsPath')
    secondLevelUserTweetsFile = config.get('output', 'secondLevelUserTweetsFile')
    maxScrollDownTimes = config.get('settings', 'maxScrollDownTimes')
    firstLevelUsersFile = config.get('data', 'firstLevelUserFile')
    userId = config.get('search', 'userId')
    urlPrefix = config.get('settings', 'urlPrefix')
    translateTargetLanguage = config.get('settings', 'translateTargetLanguage')


    tb = TwitterBot(email, password, userName, maxScrollDownTimes, firstLevelUserTweetsFile, secondLevelUserTweetsFile, urlPrefix, translateTargetLanguage)
    tb.loginAbnormal()

    # 获得一级用户列表['dawn_wei_tan', 'dansoncj', ...]
    firstLevelUsers = readCSVToGetTwitterUserLink(firstLevelUsersFile)

    # 获取一级用户主页的所有Tweets并将tweets写入外部文件
    firstLevelTweets = tb.getAndWriteUserTweets(firstLevelUsers, firstLevelUserTweetsFile)
    # time.sleep(5)

    # 获得二级用户列表
    secondLevelUsers = tb.getSecondLevelUsers(firstLevelUsers)

    # 获取二级用户主页所有Tweets并将tweets写入外部文件
    secondLevelTweets = tb.getAndWriteUserTweets(secondLevelUsers, secondLevelUserTweetsFile)
