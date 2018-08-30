# -*- coding: utf-8 -*-
import os, sys,datetime
from lxml import html
from pyquery import PyQuery as pq
import urllib
import json
import urllib2
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import loghelper
import util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

#logger
loghelper.init_logger("crawler_sogou_icp", stream=True)
logger = loghelper.get_logger("crawler_sogou_icp")

class SogouCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, use_proxy=True, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=use_proxy, timeout=timeout)
        self.headers = {
            "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9',
            "Referer": 'http://weixin.sogou.com/',
            'Host': 'weixin.sogou.com',
        }
    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)
        # logger.info(content)
        if content.find("用户您好，您的访问过于频繁，为确认本次访问为正常用户行为，需要您协助验证") >= 0 or \
           content.find("sendLog(\'verify_page\'") >= 0 :
            logger.info("Need Verfication Now!")
            logger.info(content)
            return False
        if url.find("weixin.sogou") >= 0 and title.find("搜狗微信搜索") >= 0:
            return True
        # logger.info(content)
        return False

    def get(self, url, name):

        while True:
            result = self.crawl(url, headers=self.headers)
            if result["get"] == "success":
                # logger.info(result["content"])
                if result["content"] is not None and \
                   result["content"].find("用户您好，您的访问过于频繁，为确认本次访问为正常用户行为，需要您协助验证") != -1 or \
                   result["content"].find("sendLog(\'verify_page\'") >= 0:
                    for cookie in self.cookiejar:
                        logger.info("Get Cookie step1: %s, %s", cookie.name, cookie.value)
                    code = self.handle_verify_code(result["content"])
                    logger.info("Input code is %s", code)
                    return None
                elif result["content"] is not None and result["content"].find(name) != -1:
                    return result["content"]

    def handle_verify_code(self, content):
        while True:
            try:
                for cookie in self.cookiejar:
                    logger.info("Get Cookie step4: %s, %s", cookie.name, cookie.value)
                anti_url = "http://weixin.sogou.com/antispider/"
                d = pq(html.fromstring(content.decode("utf-8")))
                # vf_url = d('img#seccodeImage').attr("href")
                iptext = d('p.ip-time-p').text()
                if iptext is None or iptext.strip() == "":
                    while True:
                        try:
                            logger.info("Reget info from: %s", anti_url)
                            request = urllib2.Request(anti_url, headers=self.headers)
                            r = self.opener.open(request, timeout=20)
                            content = r.read()
                            # logger.info(content)
                            for cookie in self.cookiejar:
                                logger.info("Get Cookie step3: %s, %s", cookie.name, cookie.value)
                            # os._exit(0)
                            break
                        except Exception,e:
                            logger.info(e)
                    # exit()
                    continue
                logger.info("Ip info :%s",iptext)
                vf = d('img#seccodeImage').attr("src")
                vfcode_url = "http://weixin.sogou.com/antispider/%s" % vf
                logger.info("Downloading verification code pic: %s", vfcode_url)
                request = urllib2.Request(vfcode_url, headers=self.headers)
                r = self.opener.open(request, timeout=20)
                s = r.read()
                for cookie in self.cookiejar:
                    logger.info("Get Cookie step2: %s, %s", cookie.name, cookie.value)
                img_path = "wechat_verf/code.png"
                with open(img_path, mode='wb') as fp:
                    fp.write(s)
                    fp.close()
                logger.info("Saved verification code to %s", format(os.path.dirname(img_path)))
                break
            except Exception, e:
                logger.info(e)
        self.vcode = raw_input("Please input the captcha:\n")
        return self.vcode

    def search_by_wechat(self, name, page=1):

        request_url = 'http://weixin.sogou.com/weixin?query=%s&_sug_type_=&_sug_=n&type=1&page=%s&ie=utf8' % (urllib.quote(name), page)
        text = None
        while True:
            try:
                text = self.get(request_url, name)
                break
            except Exception, ex:
                logger.exception(ex)

        return text

    def query_by_wechat(self, wechatId):
        gzhs = []
        content = self.search_by_wechat(wechatId)
        logger.info(content)
        #todo None how to deal with
        if content is None:
            return gzhs
        d = pq(html.fromstring(content.decode("utf-8")))
        infos = d('div.news-box> ul.news-list2> li')
        for info in infos:
            e = pq(info)
            url = e('div.gzh-box2> div> a').attr("href")
            img_url = e('div.gzh-box2> div> a> img').attr("src")
            name = e('div.txt-box> p.tit> a').text().replace(" ", "").strip()
            wechat_id = e('div.txt-box> p.info> label').text().strip()
            (description, authentication) = (None, None)
            sp3s = e('dl')
            for sp3 in sp3s:
                sp3text = pq(sp3).text()
                if sp3text.find("功能介绍") != -1:
                    description = pq(sp3)('dd').text()
                elif sp3text.find("authnamewrite") != -1:
                    authentication = pq(sp3)('dd').text()
            qrcode = e('div.pos-ico> div.pos-box> img').attr("src")

            if name is not None and name.strip() != "":
                gzh = {
                    "name": name,
                    "wechatId": wechat_id,
                    "description": description,
                    "authentication": authentication,
                    "logo": img_url,
                    "wechatUrl": url,
                    "qrcode": qrcode
                }
                gzhs.append(gzh)
                logger.info("name: %s, wechatId: %s, %s", name,wechat_id,url)

        return gzhs

    def get_gzh_message(self, wechatUrl):
        # gzh_info = get_gzh_info(wechatId)
        pass



if __name__ == "__main__":
    crawler = SogouCrawler()
    name = "talk_ai"
    items = crawler.query_by_wechat(name)
    logger.info(json.dumps(items, ensure_ascii=False, cls=util.CJsonEncoder))

