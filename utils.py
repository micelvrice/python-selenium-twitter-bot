import numpy as np
import csv
import time
from selenium import webdriver
from selenium import common
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import configparser
from Tweets import *
import pandas as pd
import os.path
import deepl

config = configparser.ConfigParser(allow_no_value=True)
config.read('config.conf', encoding='utf-8')

userName = config.get('account', 'userName')
maxScrollDownTimes = int(config.get('settings', 'maxScrollDownTimes'))
userTwitterColumn = config.get('data', 'userTwitterColumn')

def write_csv(path, data):
    np.savetxt(path, data, delimiter=',', fmt='% s')
    
def read_csv(path):
    with open(path, 'r') as f:
        reader = csv.reader(f)
        result = list(reader)
    return np.array(result).squeeze().tolist()

# 向下滚动指定次数
def scrollDown(bot):
    scrollDown = 'return document.body.scrollHeight'
    height = 0
    scrollDownTimes = 0
    while True:
        new_height = bot.execute_script(scrollDown)
        if (new_height > height) and (scrollDownTimes <= maxScrollDownTimes):
            bot.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            height = new_height
            time.sleep(5)
            scrollDownTimes += 1
        else:
            break

def findKeysFromTweets(keys, tweetsList):
    return



# 爬取某person下的tweets
# bot为经过滑动处理的用户主页https://twitter.com/realcaixia
# 返回结果为[Tweets]
def getUserTweets(bot, person):
    # 该xpath下有两个div，第一个div包含用户名和发帖时间，第二个div为帖子内容
    locationAndTimeList = bot.find_elements(By.XPATH, r'//div[@class="css-1dbjc4n r-1iusvr4 r-16y2uox r-1777fci r-kzbkwu"]/div[1]')
    articlesList = bot.find_elements(By.XPATH, r'//div[@class="css-1dbjc4n r-1iusvr4 r-16y2uox r-1777fci r-kzbkwu"]/div[2]')
    # 该bot下所有的推文列表
    resultList = []

    for locationAndTime, article in zip(locationAndTimeList, articlesList):
        timeAndPersonDiv = locationAndTime.find_elements(By.TAG_NAME, r'div')[0]

        # 应该只有一个time标签
        timeSpan = timeAndPersonDiv.find_elements(By.TAG_NAME, r'time')[0]
        articleSpan = article.find_elements(By.TAG_NAME, r'span')

        time = timeSpan.get_attribute('innerHTML')
        text = ''
        for _, span in enumerate(articleSpan):
            articleText = span.get_attribute('innerHTML')
            if articleText.startswith('<') or articleText.startswith('@'):
                articleText = ''
            text += articleText
            text = text.strip()
            text += ' '
        text = text.strip()
        thisTweet = Tweets(text,time,person)
        resultList.append(thisTweet)
    return resultList


# 获取某个Tweet的点赞用户推特账号List
# bot为经过滑动处理的like页面
# bot为https://twitter.com/realcaixia/status/1401129211138658308/likes
# 返回结果为[likesuser1, likesuser2]
def getLikeUser(bot, person):
    allLikeUsers = []
    userSpans = bot.find_elements(By.XPATH, r"//span[@class='css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0']")
    for span in userSpans:
        thisSpanUser = span.get_attribute('innerHTML')
        if thisSpanUser.startswith('@') and thisSpanUser != ('@' + userName) and thisSpanUser != ('@' + person):
            allLikeUsers.append(thisSpanUser[1:])
    return allLikeUsers

def getCommentUsers(bot, person):
    allCommentUsers = []
    userSpans = bot.find_elements(By.XPATH, r"//span[@class='css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0']")
    for span in userSpans:
        thisSpanUser = span.get_attribute('innerHTML')
        if thisSpanUser.startswith('@') and thisSpanUser != ('@' + userName) and thisSpanUser != ('@' + person):
            allCommentUsers.append(thisSpanUser[1:])
    return allCommentUsers

# 获取某用户主页下的每条推文的链接以及该推文的点赞链接
# bot为经过滑动处理的用户主页
# bot为'https://twitter.com/realcaixia'
# urls_after为推文链接List['https://twitter.com/realcaixia/status/1401129211138658308']
# urls_likes为推文的点赞链接List['https://twitter.com/realcaixia/status/1401129211138658308/likes']
def getUserTweetsAndLikesLink(bot):
    # 每个推文的链接
    urls_before = bot.find_elements(By.XPATH, r'//a[@class="css-4rbku5 css-18t94o4 css-901oao r-14j79pv r-1loqt21 r-xoduu5 r-1q142lx r-1w6e6rj r-37j5jr r-a023e6 r-16dba41 r-9aw3ui r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0"]')
    urls_after = []
    urls_likes = []
    for url in urls_before:
        urlArray = url.get_attribute('href')
        urls_after.append(urlArray)
        urlLikes = urlArray + '/' + 'likes'
        urls_likes.append(urlLikes)
    return urls_after, urls_likes

# 从外部文件中读取推特用户的主页链接https://twitter.com/userid
# 返回用户名字List
def readCSVToGetTwitterUserLink(file):
    allData = pd.read_excel(file)
    TwitterUserLink = allData.loc[:, userTwitterColumn].tolist()
    while np.nan in TwitterUserLink:
        TwitterUserLink.remove(np.nan)
    for i, _ in enumerate(TwitterUserLink):
        TwitterUserLink[i] = TwitterUserLink[i].split('/')[-1]
    return TwitterUserLink
    
def writeTweetsToCSV(TweetsList, outputFile):
    if not os.path.isfile(outputFile):
        print('待写入的外部文件不存在！！！')
    else:
        existData = pd.read_excel(outputFile)
        for tweet in TweetsList:
            toWriteData = pd.DataFrame([(tweet.person, tweet.time, tweet.text)], columns=['Person', 'Time', 'Text'])
            newData = pd.concat([existData, toWriteData])
            newData.to_excel(outputFile, index=False, engine='openpyxl')
            existData = newData

def translateToZH(sourceText):
    # 该key不要泄露
    auth_key = 'c4953a25-5ca7-3b65-c0bd-0823b102977d:fx'
    translator = deepl.Translator(auth_key)
    result = translator.translate_text(sourceText, traget_lang="ZH")
    return result


# 从keysFile中读入敏感关键词列表
# 从sourceFile读入原始全部推文
# targetFile为text中包含敏感关键词的推文文件
def filtTweets(sourceFile, targetFile, keysFile):
