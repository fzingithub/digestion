# -*- coding: utf-8 -*-
from common import helper
import urllib
import configparser
import logging
import re
import ssl

conf = configparser.ConfigParser()
conf.read("config/mysql.conf")
logger = logging.getLogger(__name__)


class Mint(object):
    def __init__(self):
        self.pagePattern = '.*?<span>共([0-9]+)页.*?</span>'
        self.listPattern = '.*?<li>.*?<a href="(.*?)".*?<img src="(.*?)".*?<h3>(.*?)</h3>.*?</li>'
        ssl._create_default_https_context = ssl._create_unverified_context

    def getHtmlBody(self, url):
        urlResponse = urllib.request.urlopen(url)
        urlBody = urlResponse.read().decode('utf-8')
        return urlBody

    def climbData(self, pattern, url):
        logger.info(url)
        htmlBody = self.getHtmlBody(url)
        textList = re.findall(pattern, htmlBody, re.S)
        return textList

    def insertDB(self, allData):
        sql = "INSERT INTO food_list(food_name, detail_url, img_url, food_type) VALUES (%s, %s, %s, %s)"
        helper.DB().insert_many(sql, allData)

    def climbFoodList(self, url):
        for i in range(1, 11):
            groupUrl = "%slist-%d-html" % (url, i)
            pages = int(self.climbData(self.pagePattern, groupUrl)[0])

            allData = list()

            for page in range(1, pages + 1):
                pageUrl = "%s?page=%d" % (groupUrl, page)
                foodList = self.climbData(self.listPattern, pageUrl)
                for it in foodList:
                    allData.append((it[2], "https:" + it[0], it[1], i))

            self.insertDB(allData)

    def climbPics(self, foodList):
        imgPath = conf.get("staticPath", "img_path")
        imgData = list()
        for it in foodList:
            imgUrl = it['img_url']
            foodId = it['food_id']
            foodType = it['food_type']

            localImgUrl = "food_type_{}/image_{}.jpg".format(foodType, foodId)

            logger.info(it)
            logger.info(localImgUrl)

            try: 
                urllib.request.urlretrieve(
                    imgUrl, "{}{}".format(imgPath, localImgUrl))
                imgData.append((foodId, localImgUrl))
            except Exception as e:
                imgData.append((foodId, ''))
                logger.error(e)
        return imgData

    def myMain(self):
        foodList = helper.DB().fetch_all("SELECT * FROM food_list")
        imgData = self.climbPics(foodList)
        helper.DB().insert_many(
            "INSERT INTO image_list(food_id, img_url) VALUES (%s, %s)", imgData)
