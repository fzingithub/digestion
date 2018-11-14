from django.test import TestCase

# Create your tests here.
from .climb import Mint

class ClimbTests(TestCase):
    def testHtmlBody(self):
        url = "http://www.boohee.com/food/group/1"
        Mint().getHtmlBody(url)
    def testClimbData(self):
        url = "http://www.boohee.com/food/group/1"
        Mint().climbData("", url)
    def testCreateUrls(self):
        Mint().allFoodData()
