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
import Tweets

config = configparser.ConfigParser(allow_no_value=True)
config.read('config.conf')

userName = config.get('account', 'userName')
maxScrollDownTimes = int(config.get('settings', 'maxScrollDownTimes'))

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
# bot为经过滑动处理的用户主页
def getUserTweets(bot, person):
    # 该xpath下有两个div，第一个div包含用户名和发帖时间，第二个div为帖子内容
    articlesList = bot.find_elements(By.XPATH, r'//div[@class="css-1dbjc4n r-1iusvr4 r-16y2uox r-1777fci r-kzbkwu"]')

    # 该bot下所有的推文列表
    resultList = []
    for _, article in enumerate(articlesList):
        timeAndPersonDiv = article.find_elements(By.TAG_NAME, r'div')[0]
        textDiv = article.find_elements(By.TAG_NAME, r'div')[1]

        # 应该只有一个time标签
        timeSpan = timeAndPersonDiv.find_elements(By.TAG_NAME, r'time')[0]
        articleSpan = textDiv.find_elements(By.TAG_NAME, r'span')

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
        resultList.append(Tweets(text, time, person))
    return resultList


# 获取某个Tweet的点赞用户推特账号List
# bot为经过滑动处理的like页面
def getLikeUser(bot):
    allLikeUsers = []
    userSpans = bot.find_elements(By.XPATH, r"//span[@class='css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0']")
    for span in userSpans:
        thisSpanUser = span.get_attribute('innerHTML')
        if thisSpanUser.startswith('@') and thisSpanUser != ('@' + userName):
            allLikeUsers.append(thisSpanUser)
    return allLikeUsers

# 获取某用户主页下的每天推文的链接
# bot为经过滑动处理的用户主页
def getUserTweetsLink(bot):
    artcleLinkeList = bot.find_elements(By.XPATH, r'//a[@class="css-4rbku5 css-18t94o4 css-901oao r-14j79pv r-1loqt21 r-xoduu5 r-1q142lx r-1w6e6rj r-37j5jr r-a023e6 r-16dba41 r-9aw3ui r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0"]')






