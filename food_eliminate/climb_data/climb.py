# -*- coding: utf-8 -*-
from urllib import request
from common import helper
import logging
import re
import ssl


logger = logging.getLogger(__name__)


class Mint(object):
    def __init__(self):
        self.pagePattern = '.*?<span>共([0-9]+)页.*?</span>'
        self.listPattern = '.*?<li>.*?<a href="(.*?)".*?<img src="(.*?)".*?<h3>(.*?)</h3>.*?</li>'

    def getHtmlBody(self, url):
        ssl._create_default_https_context = ssl._create_unverified_context
        urlResponse = request.urlopen(url)
        urlBody = urlResponse.read().decode('utf-8')
        return urlBody

    def climbData(self, pattern, url):
        logger.info(url)
        htmlBody = self.getHtmlBody(url)
        textList = re.findall(pattern, htmlBody, re.S)
        return textList

    def insertDB(self, allData):
        sql = "INSERT INTO food_list(food_name, detail_url, pic_url) VALUES (%s, %s, %s)"
        helper.DB().insert_many(sql, allData)

    def allFoodData(self):
        url = "https://food.hiyd.com/"

        for i in range(1, 11):
            groupUrl = "%slist-%d-html" % (url, i)
            pages = self.climbData(self.pagePattern, groupUrl)
            for page in range(1, int(pages[0]) + 1):
                pageUrl = "%s?page=%d" % (groupUrl, page)
                foodList = self.climbData(self.listPattern, pageUrl)

                allData = list()
                for it in foodList:
                    allData.append((it[2], "https:" + it[0], it[1]))
                self.insertDB(allData)
