class TwitterUser:
    def __init__(self, userId, userTweets, userLocation, userInformation):
        # 用户id String
        self.userId = userId

        # 用户近期推文 List
        self.userTweets = userTweets

        # 用户所在位置 String
        self.userLocation = userLocation  

        # 用户主页简介 String
        self.userInformation = userInformation
    def printUser(self):
        print(self.userId + self.userTweets + self.userLocation + self.userInformation)