from django.test import TestCase

# Create your tests here.
from .climb import Mint


class ClimbTests(TestCase):
    url = "http://www.boohee.com/food/group/1"

    def testHtmlBody(self):
        Mint().getHtmlBody(self.url)

    def testClimbData(self):
        Mint().climbData("", self.url)

    def testCreateUrls(self):
        Mint().climbFoodList(self.url)

    def testClimbPics(self):
        Mint().climbPics(self.url)

    def testMyMain(self):
        Mint().myMain()
