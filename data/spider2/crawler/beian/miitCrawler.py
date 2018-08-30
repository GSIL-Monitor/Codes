# -*- coding: utf-8 -*-
import os, sys, datetime, re, json
import random
import urllib2, urllib
import time
from lxml import html
from pyquery import PyQuery as pq
import selenium
from selenium import webdriver
from pyvirtualdisplay import Display

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,db, util,url_helper

#logger
loghelper.init_logger("crawler_miit", stream=True)
logger = loghelper.get_logger("crawler_miit")


class miitCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, max_crawl=1, timeout=30, use_proxy=False):
        BaseCrawler.BaseCrawler.__init__(self, max_crawl=max_crawl, timeout=timeout, use_proxy=use_proxy)

        self._post_url = 'http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_searchExecute.action'

        self.token = None
        self.jsessionid = None
        self._jsl_clearance = None
        self._jsluid = None
        self.bduss = ''
        self.agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:49.0) Gecko/20100101 Firefox/49.0"
        self.vcode = None

        self.headers = {
            "User-Agent": self.agent,
            'Host': "www.miitbeian.gov.cn",
        }

    def _get_jsl_clearance(self):
        while True:
            try:
                profile_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], "profile")
                # logger.info(profile_dir)
                fp = webdriver.FirefoxProfile(profile_dir)
                fp.update_preferences()
                driver = webdriver.Firefox()
                logger.info("driver start")
                driver.implicitly_wait(30)
                driver.set_page_load_timeout(30)
                driver.set_script_timeout(30)
                driver.get(self._post_url)
                time.sleep(4)
                # logger.info(driver.get_cookies())
                cookies = driver.get_cookies()
                logger.info(cookies)
                driver.quit()
                for cookie in cookies:
                    if cookie["name"] == "__jsluid":
                        self._jsluid = cookie["value"]
                    elif cookie["name"] == "__jsl_clearance":
                        self._jsl_clearance = cookie["value"]

                if self._jsluid is not None and self._jsl_clearance is not None:
                    break

            except selenium.common.exceptions.TimeoutException, exception:
                logger.info("Timeout")
                break
            except selenium.common.exceptions.WebDriverException, exception:
                logger.info(exception)

        logger.info("Get jsluid: %s", self._jsluid)
        logger.info("Get jsl_clearance: %s", self._jsl_clearance)


    def _get_jsessionid(self):
        """Get JSESSIONID."""
        while True:
            try:
                self.headers["Cookie"] = "__jsluid=%s; __jsl_clearance=%s" % (self._jsluid, self._jsl_clearance)
                request = urllib2.Request(self._post_url, headers=self.headers)
                r = self.opener.open(request, timeout=20)
                for cookie in self.cookiejar:
                    logger.info("Get Cookie step1: %s, %s", cookie.name, cookie.value)
                    if cookie.name == "JSESSIONID":
                        self.jsessionid = cookie.value
                if self.jsessionid is not None:
                    break
            except Exception,e:
                logger.info(e)

        return self.jsessionid

    def _handle_verify_code(self):
        """Save verify code to filesystem and prompt user to input."""
        while True:
            # r = self.session.get(self._genimage_url.format(code=self.codestring))
            try:
                self.headers["Cookie"] = "__jsluid=%s; __jsl_clearance=%s; JSESSIONID=%s" % (self._jsluid, self._jsl_clearance, self.jsessionid)
                vfcode_url = "http://www.miitbeian.gov.cn/getVerifyCode?%s" % random.randint(10, 90)
                logger.info("Downloading verification code pic: %s", vfcode_url)
                request = urllib2.Request(vfcode_url,headers=self.headers)
                r = self.opener.open(request, timeout=20)
                s = r.read()
                for cookie in self.cookiejar:
                    logger.info("Get Cookie step2: %s, %s", cookie.name, cookie.value)
                    if cookie.name == "JSESSIONID":
                        self.jsessionid = cookie.value
                img_path = "miitVerf/code.png"
                with open(img_path, mode='wb') as fp:
                    fp.write(s)
                    fp.close()
                logger.info("Saved verification code to %s", format(os.path.dirname(img_path)))
                break
            except Exception,e:
                logger.info(e)
        self.vcode = raw_input("Please input the captcha:\n")
        return self.vcode

    def _validCode(self):
        flag = False

        try:
            logger.info("Valid code=%s", self.vcode)
            valid_url = "http://www.miitbeian.gov.cn/common/validate/validCode.action"
            self.headers["Cookie"] = "__jsluid=%s; __jsl_clearance=%s; JSESSIONID=%s" % (self._jsluid, self._jsl_clearance, self.jsessionid)
            post_data = {'validateValue': self.vcode}
            post_data = urllib.urlencode(post_data)
            request = urllib2.Request(valid_url, data=post_data, headers=self.headers)
            r = self.opener.open(request, timeout=20)
            s = r.read()
            for cookie in self.cookiejar:
                logger.info("Get Cookie step3: %s, %s", cookie.name, cookie.value)
                if cookie.name == "JSESSIONID":
                    self.jsessionid = cookie.value
            logger.info("Valid content: %s", s)
            try:
                result = json.loads(s)
                # logger.info(result)
                if result.has_key("result") is True and result["result"] is True:
                    logger.info("Valid is right!!!!")
                    flag = True
            except Exception, e:
                logger.info(e)

        except Exception, e:
            logger.info(e)

        return flag

    def verf(self):
        logger.info("verfing!!!!")
        self.init_http_session(self._post_url)

        self._get_jsl_clearance()
        self._get_jsessionid()

        while True:
            vcode = self._handle_verify_code()
            result = self._validCode()
            if result is True:
                break

    def parse_query(self,content):
        # logger.info(content)
        d = pq(html.fromstring(content.decode("gbk")))
        trs = d('td.a> table> tr')

        for tr in trs:
            try:
                info = pq(tr)
                # logger.info(info)
                tds = info('td')
                if len(tds)<8:
                    continue
                organizer = pq(tds[1]).text().strip()
                if organizer == "主办单位名称":
                    continue
                organizertype = pq(tds[2]).text().strip()
                beianhao = pq(tds[3]).text().strip()
                websiteName = pq(tds[4]).text().strip()
                homepage = pq(tds[5]).text().strip()
                # beianDate = datetime.datetime.strptime(pq(tds[6]).text().strip(), "%Y-%m-%d")
                beianDate = pq(tds[6]).text().strip()

                # item_new = {
                #     "domain": ,
                #     "organizer": organizer,
                #     "organizerType": organizertype,
                #     "beianhao": beianhao_new,
                #     "mainBeianhao": mainBeianhao,
                #     "websiteName": websiteName_new,
                #     "homepage": homepage_new,
                #     "beianDate": beianDate_new,

                logger.info("%s, %s, %s, %s, %s, %s", organizer, organizertype, beianhao, websiteName, homepage, beianDate)
            except Exception, e:
                logger.info(e)



    def query_by_url(self, postdata):
        self.verf()
        url = "%s;jsessionid=%s" % (self._post_url, self.jsessionid)
        postdata["verifyCode"] =  self.vcode
        logger.info(postdata)
        postdata = urllib.urlencode(postdata)
        self.headers["Cookie"] = "__jsluid=%s; __jsl_clearance=%s; JSESSIONID=%s" % (self._jsluid, self._jsl_clearance, self.jsessionid)
        while True:
            try:
                request = urllib2.Request(url, data=postdata, headers=self.headers)
                r = self.opener.open(request, timeout=20)
                s = r.read()
                logger.info("Login Content get!")
                self.parse_query(s)
                break
            except Exception, e:
                logger.info("Wrong here")
                logger.info(e)

    def query_by_domain(self, domain):
        data = {
            "siteName": "",
            "condition": "1",
            "siteDomain": domain,
            "siteUrl": "",
            "mainLicense": "",
            "sitelp": "",
            "unitName": "",
            "mainUnitNature": "-1",
            "certType": "-1",
            "mainUnitCertNo": "",
        }
        self.query_by_url(data)


if __name__ == "__main__":
    # display = Display(visible=0, size=(1280, 800))
    # display.start()
    # time.sleep(5)
    miit = miitCrawler()
    miit.query_by_domain("teambition.com")
    # result = baidu.crawl("https://www.baidu.com/")
    # display.stop()
    pass