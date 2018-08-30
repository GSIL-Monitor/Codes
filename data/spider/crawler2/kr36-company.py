# -*- coding: utf-8 -*-
import os, sys
import time, random
from BaseCrawler import BaseCrawler
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper

#logger
loghelper.init_logger("crawler_itjuzi_company", stream=True)
logger = loghelper.get_logger("crawler_itjuzi_company")

SOURCE = 13020  #36kr
TYPE = 36001    #公司信息

login_users = [
    #{"name":"daffy@mailinator.com", "pwd":"daffy123"},
    #{"name":"minnie@mailinator.com", "pwd":"minnie"},
    #{"name":"elmer@mailinator.com", "pwd":"elmer123"},
    #{"name":"tweety@mailinator.com", "pwd":"tweety"},
    #{"name":"alfonse@mailinator.com", "pwd":"alfonse"},
    {"name":"alice@mailinator.com","pwd":"123456"},
    {"name":"anna@mailinator.com","pwd":"123456"},
    {"name":"annie@mailinator.com","pwd":"123456"},
    {"name":"barbara@mailinator.com","pwd":"123456"},
    {"name":"bernice@mailinator.com","pwd":"123456"},
    {"name":"dolores@mailinator.com","pwd":"123456"},
    {"name":"doris@mailinator.com","pwd":"123456"},
    {"name":"dorothy@mailinator.com","pwd":"123456"},
    {"name":"edith@mailinator.com","pwd":"123456"},
    {"name":"edna@mailinator.com","pwd":"123456"},
    {"name":"eleanor@mailinator.com","pwd":"123456"},
    {"name":"elizabeth@mailinator.com","pwd":"123456"},
    {"name":"ethel@mailinator.com","pwd":"123456"},
    {"name":"evelyn@mailinator.com","pwd":"123456"},
    {"name":"florence@mailinator.com","pwd":"123456"},
    {"name":"frances@mailinator.com","pwd":"123456"},
    {"name":"gladys@mailinator.com","pwd":"123456"},
    {"name":"gloria@mailinator.com","pwd":"123456"},
    {"name":"grace@mailinator.com","pwd":"123456"},
    {"name":"hazel@mailinator.com","pwd":"123456"},
    {"name":"Arthur123@mailinator.com","pwd":"123456"},
    {"name":"Arthur1234@mailinator.com","pwd":"123456"},
    {"name":"Arthur1235@mailinator.com","pwd":"123456"},
    {"name":"Arthur1236@mailinator.com","pwd":"123456"},
    {"name":"Arthur1237@mailinator.com","pwd":"123456"},
    {"name":"Arthur1238@mailinator.com","pwd":"123456"},
    {"name":"Arthur1239@mailinator.com","pwd":"123456"},
    {"name":"Arthur1240@mailinator.com","pwd":"123456"},
    {"name":"Arthur1241@mailinator.com","pwd":"123456"},
    {"name":"Arthur1242@mailinator.com","pwd":"123456"},
    {"name":"Arthur1243@mailinator.com","pwd":"123456"},
    {"name":"Arthur1244@mailinator.com","pwd":"123456"},
    {"name":"Arthur1245@mailinator.com","pwd":"123456"},
    {"name":"Arthur1246@mailinator.com","pwd":"123456"},
    {"name":"Arthur1247@mailinator.com","pwd":"123456"},
    {"name":"Arthur1248@mailinator.com","pwd":"123456"},
    {"name":"Arthur1249@mailinator.com","pwd":"123456"},
    {"name":"Arthur1250@mailinator.com","pwd":"123456"},
    {"name":"Arthur1251@mailinator.com","pwd":"123456"},
    {"name":"Arthur1252@mailinator.com","pwd":"123456"},
    {"name":"Arthur1253@mailinator.com","pwd":"123456"},
    {"name":"Arthur1254@mailinator.com","pwd":"123456"},
    {"name":"Arthur1255@mailinator.com","pwd":"123456"},
    {"name":"Arthur1256@mailinator.com","pwd":"123456"},
    {"name":"Arthur1257@mailinator.com","pwd":"123456"},
    {"name":"Arthur1258@mailinator.com","pwd":"123456"},
    {"name":"Arthur1259@mailinator.com","pwd":"123456"},
    {"name":"Arthur1260@mailinator.com","pwd":"123456"},
    {"name":"Arthur1261@mailinator.com","pwd":"123456"},
    {"name":"Arthur1262@mailinator.com","pwd":"123456"},
    {"name":"Arthur1263@mailinator.com","pwd":"123456"},
    {"name":"Arthur1264@mailinator.com","pwd":"123456"},
    {"name":"Arthur1265@mailinator.com","pwd":"123456"},
    {"name":"Arthur1266@mailinator.com","pwd":"123456"},
    {"name":"Arthur1267@mailinator.com","pwd":"123456"},
    {"name":"Arthur1268@mailinator.com","pwd":"123456"},
    {"name":"Arthur1269@mailinator.com","pwd":"123456"},
    {"name":"Arthur1270@mailinator.com","pwd":"123456"},
    {"name":"Arthur1271@mailinator.com","pwd":"123456"},
    {"name":"Arthur1272@mailinator.com","pwd":"123456"},
    {"name":"Arthur1273@mailinator.com","pwd":"123456"},
    {"name":"Arthur1274@mailinator.com","pwd":"123456"},
    {"name":"Arthur1275@mailinator.com","pwd":"123456"},
    {"name":"Arthur1276@mailinator.com","pwd":"123456"},
    {"name":"Arthur1277@mailinator.com","pwd":"123456"},
    {"name":"Arthur1278@mailinator.com","pwd":"123456"},
    {"name":"Arthur1279@mailinator.com","pwd":"123456"},
    {"name":"Arthur1280@mailinator.com","pwd":"123456"},
    {"name":"Arthur1281@mailinator.com","pwd":"123456"},
    {"name":"Arthur1282@mailinator.com","pwd":"123456"},
]

class Kr36Crawler(BaseCrawler):
    def __init__(self, start):
        BaseCrawler.__init__(self, max_crawl=20)
        self.set_start(start)

    def set_start(self, start):
        self.current = start
        self.latest = start

    def get_url(self):
        url  = {}
        key = str(self.current)
        url["key"] = key
        url["company_base"] = "http://rong.36kr.com/api/company/%s" % key
        url["past_finance"] = "http://rong.36kr.com/api/company/%s/past-finance" % key
        url["past_investor"] = "http://rong.36kr.com/api/company/%s/past-investor?pageSize=100" % key
        url["funds"]  = "http://rong.36kr.com/api/company/%s/funds" % key
        url["product"] = "http://rong.36kr.com/api/company/%s/product" % key
        url["past_investment"] = "http://rong.36kr.com/api/company/%s/past-investment" % key
        url["company_fa"] = "http://rong.36kr.com/api/fa/company-fa?cid=%s" % key
        url["founders"] = "http://rong.36kr.com/api/company/%s/founder?pageSize=1000" % key
        url["employees"] = "http://rong.36kr.com/api/company/%s/employee?pageSize=1000" % key
        url["former_members"] = "http://rong.36kr.com/api/company/%s/former-member?pageSize=1000" % key

        self.current += 1
        return url

    #实现
    def has_content(self, r):
        if r is not None and r.status_code == 200:
            try:
                j = r.json()
            except:
                logger.info("Not json content")
                logger.info(r.text)
                return False

            if j["code"] == 0:
                return True
            else:
                logger.info("code=%d, %s" %(j["code"], j["msg"]))
        else:
            logger.info("Fail to get content")
            if r is not None:
                logger.info("status_code=%d" % r.status_code)

        return False

    def isBusy(self, r):
        if r is not None and r.status_code == 200:
            try:
                j = r.json()
            except:
                #logger.info("Not json content")
                #logger.info(r.text)
                return False

            if j["msg"].strip() == "您请求的过于频繁，请稍后再试！":
                logger.info("code=%d, %s" %(j["code"], j["msg"]))
                return True

        return False

    def process(self, url, key, company):
        #logger.info(company)
        self.save(SOURCE, TYPE, url, key, company)
        self.latest = self.current-1

    def is_end(self):
        if self.latest < self.current - 100 and self.current > 130000:
            return True
        return False

    def login(self, url):
        while True:
            self.init_http_session(url)

            idx = random.randint(0, len(login_users)-1)
            login_user = login_users[idx]
            logger.info(login_user)

            data = {
                "type":"login",
                "bind":False,
                "needCaptcha":False,
                "username":login_user["name"],
                "password":login_user["pwd"],
                "ok_url":"/"

            }
            headers = {
                "Referer":"http://passport.36kr.com"
            }

            try:
                r = self.http_session.post("http://passport.36kr.com/passport/sign_in",data=data, headers=headers, timeout=20)
                logger.info(r.text)
            except:
                continue

            if r.status_code != 200:
                continue

            if r.text.strip() != '{"redirect_to":"/"}':
                continue

            try:
                r = self.http_session.get("http://uc.36kr.com/api/user/identity", timeout=20)
            except:
                continue

            if r.status_code == 200:
                try:
                    result = r.json()
                except:
                    logger.info(r.text)
                    continue
                logger.info(result)
                if result["code"] == 4031:
                    break


if __name__ == "__main__":
    logger.info("Start...")

    flag = "incr"
    if len(sys.argv) > 1:
        flag = sys.argv[1]

    start = 1
    t = Kr36Crawler(start)

    if flag == "incr":
        latest = t.get_latest_key_int(SOURCE, TYPE)
        if latest is not None:
            start = latest + 1
            t.set_start(start)

    while True:
        url_map = t.get_url()
        key = url_map["key"]

        while True:
            r = t.crawl(url_map["company_base"])
            if t.isBusy(r):
                t.login(url_map["company_base"])
            else:
                break

        if t.has_content(r):
            company = {}
            company_base = r.json()
            company["company_base"] = company_base
            logger.info(company_base["data"]["company"]["name"])

            for k in url_map.keys():
                if k != "key" and k != "company_base":
                    while True:
                        r = t.crawl(url_map[k])
                        if t.isBusy(r):
                            r = t.crawl(url_map[k])
                        else:
                            break
                    if t.has_content(r):
                        company[k] = r.json()
                    #time.sleep(random.randint(3,8))

            t.process(url_map["company_base"], key, company)

        #no data in this range
        if t.current > 35395 and t.current < 130721:
            t.current = 130721
            t.latest = t.current

        if t.is_end():
            break

        #time.sleep(random.randint(3,8))

    logger.info("End.")
