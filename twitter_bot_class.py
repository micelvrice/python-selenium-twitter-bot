from selenium import webdriver
from selenium import common
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
from utils import *
import numpy as np
from TwitterUser import *




# https://zhuanlan.zhihu.com/p/60852696
option = webdriver.ChromeOptions()
option.add_argument('--disable-gpu')
option.add_argument('--start-maximized')
option.add_argument('blink-settings=imagesEnabled=false')
prefs = {
    'profile.default_content_setting_values' : {
        'notifications' : 2
    }
}
# 保持页面登录状态
option.add_argument(r'user-data-dir=C:\Users\LY\AppData\Local\Google\Chrome\User Data')
option.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(chrome_options=option)
driver.implicitly_wait(30)
driver.maximize_window()
class TwitterBot:

    """
    A Bot class that provide features of:
        - Logging into your Twitter account
        - Liking tweets of your homepage
        - Searching for some keyword or hashtag
        - Liking tweets of the search results
        - Posting tweets
        - Logging out of your account

    ........

    Attributes
    ----------
    email : str
        user email for Twitter account
    password : str
        user password for Twitter account
    bot : WebDriver
        webdriver that carry out the automation tasks
    is_logged_in : bool
        boolean to check if the user is logged in or not

    Methods
    -------
    login()
        logs user in based on email and password provided during initialisation
    logout()
        logs user out
    search(query: str)
        searches for the provided query string
    like_tweets(cycles: int)
        loops over number of cycles provided, scrolls the page down and likes the available tweets on the page in each loop pass
    """
    

    def __init__(self, email, password, userName, maxScrollDownTimes, outputTweetsPath, urlPrefix, translateTargetLanguage):
        self.email = email
        self.password = password
        self.userName = userName
        self.bot = driver
        self.outputTweetsPath = outputTweetsPath
        self.maxScrollDownTimes = maxScrollDownTimes
        self.urlPrefix = urlPrefix
        self.translateTargetLanguage = translateTargetLanguage
        self.is_logged_in = False


    def loginNormal(self):
        bot = self.bot
        bot.get('https://twitter.com/i/flow/login')

        emailInput = bot.find_element(By.NAME, r'text')
        emailInput.clear()
        emailInput.send_keys(self.email)

        time.sleep(2)

        nextStepButton = bot.find_element(By.XPATH, r'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div')
        nextStepButton.click()

        passwdInput = bot.find_element(By.NAME, r'password')
        passwdInput.clear()
        passwdInput.send_keys(self.password)

        loginButton = bot.find_element(By.XPATH, r'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div')
        loginButton.click()

        self.is_logged_in = True
    def loginAbnormal(self):
        bot = self.bot
        bot.get('https://twitter.com/i/flow/login')

        emailInput = bot.find_element(By.NAME, r'text')
        emailInput.clear()
        emailInput.send_keys(self.email)
        time.sleep(2)
        nextStepButton = bot.find_element(By.XPATH, r'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div')
        nextStepButton.click()

        userIdInput = bot.find_element(By.NAME, 'text')
        userIdInput.clear()
        userIdInput.send_keys(self.userName)
        userIdInput.send_keys(keys.Keys.ENTER)
        time.sleep(2)

        passwdInput = bot.find_element(By.NAME, r'password')
        passwdInput.clear()
        passwdInput.send_keys(self.password)
        passwdInput.send_keys(keys.Keys.ENTER)

        self.is_logged_in = True

    def logout(self):
        if not self.is_logged_in:
            return 

        bot = self.bot
        bot.get('https://twitter.com/home')
        time.sleep(4)

        try:
            bot.find_element_by_xpath("//div[@data-testid='SideNav_AccountSwitcher_Button']").click()
        except common.exceptions.NoSuchElementException:
            time.sleep(3)
            bot.find_element_by_xpath("//div[@data-testid='SideNav_AccountSwitcher_Button']").click()

        time.sleep(1)

        try:
            bot.find_element_by_xpath("//a[@data-testid='AccountSwitcher_Logout_Button']").click()
        except common.exceptions.NoSuchElementException:
            time.sleep(2)
            bot.find_element_by_xpath("//a[@data-testid='AccountSwitcher_Logout_Button']").click()

        time.sleep(3)

        try:
            bot.find_element_by_xpath("//div[@data-testid='confirmationSheetConfirm']").click()
        except common.exceptions.NoSuchElementException:
            time.sleep(3)
            bot.find_element_by_xpath("//div[@data-testid='confirmationSheetConfirm']").click()

        time.sleep(3) 
        self.is_logged_in = False


    # usersList为[realcaixia, JoeBiden]
    # 返回[Tweets]
    def getAndWriteUserTweets(self, usersList, outputTweetsPath):
        bot = self.bot
        TweetsList = []
        for user in usersList:
            userPage = self.urlPrefix + user
            bot.get(userPage)
            time.sleep(3)
            scrollDown(bot)
            thisUserTweetsList = getUserTweets(bot, user)
            print(len(thisUserTweetsList))
            writeTweetsToCSV(thisUserTweetsList, outputTweetsPath)
            print('----------------------正在写入----------------------')
            TweetsList.append(thisUserTweetsList)
        print('全部一级用户Tweets已写入外部文件')
        return TweetsList

    # 输入usersList为一级用户List
    # 二级用户即给一级用户点赞评论的用户
    def getSecondLevelUsers(self, usersList):
        bot = self.bot
        SecondLevelUsers = []
        for user in usersList:
            # 进入当前用户主页
            userPage = self.urlPrefix + user
            bot.get(userPage)
            scrollDown(bot)
            time.sleep(3)

            articlesLink, articlesLikesLink = getUserTweetsAndLikesLink(bot)
            for articlesLink, articlesLike in zip(articlesLink, articlesLikesLink):
                # 获取评论用户
                bot.get(articlesLink)
                scrollDown(bot)
                time.sleep(3)
                commentUsers = getCommentUsers(bot, user)

                # 获取点赞用户
                bot.get(articlesLike)
                scrollDown(bot)
                time.sleep(3)

                likeUsers = getLikeUser(bot, user)
                SecondLevelUsers.extend([item for item in likeUsers])
                SecondLevelUsers.extend([item for item in commentUsers])
            # 去重
        return list(set(SecondLevelUsers))
                
        #     # 从articlesLink中检索评论用户



    # https://twitter.com/JoeBiden 后边为用户id
    # 获取给用户userId近期推文点赞的用户id，返回list
    def searchLikesUsers(self, userId='', outputPath=''):
        bot = self.bot
        personPage = 'https://twitter.com/' + userId
        bot.get(personPage)


        time.sleep(5)
        articleList = bot.find_elements(By.XPATH, r'//a[@class="css-4rbku5 css-18t94o4 css-901oao r-14j79pv r-1loqt21 r-xoduu5 r-1q142lx r-1w6e6rj r-37j5jr r-a023e6 r-16dba41 r-9aw3ui r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0"]')
        urls_before = articleList
        # urls_before = articleList.find_elements(By.XPATH, r'//a')
        urls_after = []
        # # 推文链接为https://twitter.com/realcaixia/status/1401129211138658308
        # containKeys = userId + '/' + 'status'
        # notcontainKeys = 'photo'
        for url in urls_before:
            urlArray = url.get_attribute('href')
            urls_after.append(urlArray)
        print(urls_after)


        allUsers = []
        for url in urls_after:
            urlLikes = url + '/' + 'likes'
            bot.get(urlLikes)
            time.sleep(5)
            userSpans = bot.find_elements(By.XPATH, r"//span[@class='css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0']")
            for span in userSpans:
                thisSpanUser = span.get_attribute('innerHTML')
                if thisSpanUser.startswith('@') and thisSpanUser != ('@'+ self.userName):
                    allUsers.append(thisSpanUser)
        print('本次获取到的点赞用户数量为：')
        print(len(list(set(allUsers))))
        write_csv(outputPath, list(set(allUsers)))
        print('以将用户列表保存到本地指定路径！！！')
        return list(set(allUsers))
                
        # normal
        # urlTest = urls_after[0]
        # urlTest = 'https://twitter.com/realcaixia/status/1401129211138658308'
        # urlLike = urlTest + '/' + 'likes'
        # bot.get(urlLike)
        # time.sleep(5)

    # userIdList中的userId均以@开头
    # https://twitter.com/userId为该用户主页
    def searchForLikesUsersTweetsAndLocation(self, userIdsPath):
        bot = self.bot

        # 从本地文件读取userIdsList
        userIdsList = read_csv(userIdsPath)
        print(userIdsList)
        userIdsList = ['realcaixia', 'JoeBiden']

        userId = 'realcaixia'
        userPage = 'https://twitter.com' + '/' + userId
        bot.get(userPage)
        time.sleep(5)
        try:
            userLocationSpan = bot.find_element(By.XPATH, r'/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[4]/div/span[1]/span/span')
            userLocation = userLocationSpan.get_attribute('innerHTML')
        except:
            userLocation = 'Not Found'

        print(userLocation)

        # userInformationDiv = bot.find_element(By.XPATH, r'/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[3]/div/div[1]')
        # userInformationSpan = userInformationDiv.find_elements(By.TAG_NAME, r'span')
        # userInformation = ''
        # for span in userInformationSpan:
        #     infor = span.get_attribute('innerHTML')
        #     if infor.startswith('<a'):
        #         infor = span.find_element(By.TAG_NAME, 'a').get_attribute('innerHTML')
        #     infor = infor.strip()
        #     userInformation += infor
        #     userInformation += ' '
        
        # print(userInformation.strip())

        # 保存所有用户信息，每个元素为一个TwitterUser类
        userList = []
        for userIds in userIdsList:

            # 加载当前用户主页
            userName = userIds[1:] if userIds.startswith('@') else userIds
            userPage = 'https://twitter.com' + '/' + userName
            bot.get(userPage)
            time.sleep(5)

            # 获取Location String
            userLocationSpan = bot.find_element(By.XPATH, r'/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[4]/div/span[1]/span/span')
            userLocation = userLocationSpan.get_attribute('innerHTML') if userLocationSpan else 'Not Found'

            # 获取Information String
            userInformationDiv = bot.find_element(By.XPATH, r'/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[3]/div/div[1]')
            userInformationSpan = userInformationDiv.find_elements(By.TAG_NAME, r'span')
            userInformation = ''
            for span in userInformationSpan:
                infor = span.get_attribute('innerHTML')
                if infor.startswith('<a'):
                    infor = span.find_element(By.TAG_NAME, 'a').get_attribute('innerHTML')
                infor = infor.strip()
                userInformation += infor
                userInformation += ' '
            userInformation = userInformation.strip()

            # 获取近期推文List
            scrollDown(bot)
            articlesList = bot.find_elements(By.XPATH, r'//div[@class="css-1dbjc4n r-1iusvr4 r-16y2uox r-1777fci r-kzbkwu"]/div[2]')
            textList = []
            for _, article in enumerate(articlesList):
                articleSpan = article.find_elements(By.TAG_NAME, r'span')
                text = ''
                for _, span in enumerate(articleSpan):
                    articleText = span.get_attribute('innerHTML')
                    if articleText.startswith('<') or articleText.startswith('@'):
                        articleText = ''
                    text += articleText
                    text = text.strip()
                    text += ' '
                text = text.strip()
                # 当前用户的推文列表
                textList.append(text)
            
            thisUser = TwitterUser(userIds, textList, userLocation, userInformation)
            userList.append(thisUser)
            



        # userId = 'realcaixia'
        # userPage = 'https://twitter.com' + '/' + userId
        # bot.get(userPage)
        # time.sleep(5)
        # scrollDown(bot)
        # articlesList = bot.find_elements(By.XPATH, r'//div[@class="css-1dbjc4n r-1iusvr4 r-16y2uox r-1777fci r-kzbkwu"]/div[2]')
        # textList = []
        # for _, article in enumerate(articlesList):
        #     articleSpan = article.find_elements(By.TAG_NAME, r'span')
        #     text = ''
        #     for _, span in enumerate(articleSpan):
        #         articleText = span.get_attribute('innerHTML')
        #         if articleText.startswith('<') or articleText.startswith('@'):
        #             articleText = ''
        #         text += articleText
        #         text = text.strip()
        #         text += ' '
        #     text = text.strip()
        #     textList.append(text)
        print(userList)
        return 

# person = realcaixia
    def test(self, person):
        bot = self.bot
        url = 'https://twitter.com/' + person
        bot.get(url)
        time.sleep(5)
        scrollDown(bot)
        time.sleep(3)
        ThisUserTweets = getUserTweets(bot, person)
        print(len(ThisUserTweets))

    
        


    def like_tweets(self, cycles=10):
        if not self.is_logged_in:
            raise Exception("You must log in first!") 

        bot = self.bot   

        for i in range(cycles):
            try:
                bot.find_element_by_xpath("//div[@data-testid='like']").click()
            except common.exceptions.NoSuchElementException:
                time.sleep(3)
                bot.execute_script('window.scrollTo(0,document.body.scrollHeight/1.5)') 
                time.sleep(3)
                bot.find_element_by_xpath("//div[@data-testid='like']").click()

            time.sleep(1)
            bot.execute_script('window.scrollTo(0,document.body.scrollHeight/1.5)') 
            time.sleep(5)

      
    def post_tweets(self,tweetBody):
        if not self.is_logged_in:
            raise Exception("You must log in first!")

        bot = self.bot  

        try:
            bot.find_element_by_xpath("//a[@data-testid='SideNav_NewTweet_Button']").click()
        except common.exceptions.NoSuchElementException:
            time.sleep(3)
            bot.find_element_by_xpath("//a[@data-testid='SideNav_NewTweet_Button']").click()

        time.sleep(4) 
        body = tweetBody

        try:
            bot.find_element_by_xpath("//div[@role='textbox']").send_keys(body)
        except common.exceptions.NoSuchElementException:
            time.sleep(3)
            bot.find_element_by_xpath("//div[@role='textbox']").send_keys(body)

        time.sleep(4)
        bot.find_element_by_class_name("notranslate").send_keys(keys.Keys.ENTER)
        bot.find_element_by_xpath("//div[@data-testid='tweetButton']").click()
        time.sleep(4) 

