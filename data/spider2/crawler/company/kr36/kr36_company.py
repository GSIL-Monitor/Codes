# -*- coding: utf-8 -*-
import os, sys,random
import urllib2
import urllib
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper

#logger
loghelper.init_logger("crawler_36kr_company", stream=True)
logger = loghelper.get_logger("crawler_36kr_company")

'''
    {"name":"daffy@mailinator.com", "pwd":"daffy123"},
    {"name":"minnie@mailinator.com", "pwd":"minnie"},
    {"name":"elmer@mailinator.com", "pwd":"elmer123"},
    {"name":"tweety@mailinator.com", "pwd":"tweety"},
    {"name":"alfonse@mailinator.com", "pwd":"alfonse"},
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

    ------TEAM2
    {"name":"ann1@mailinator.com","pwd":"123456"},
    {"name":"ann2@mailinator.com","pwd":"123456"},
    {"name":"ann3@mailinator.com","pwd":"123456"},
    {"name":"ann4@mailinator.com","pwd":"123456"},
    {"name":"ann5@mailinator.com","pwd":"123456"},
    {"name":"ann6@mailinator.com","pwd":"123456"},
    {"name":"ann7@mailinator.com","pwd":"123456"},
    {"name":"ann8@mailinator.com","pwd":"123456"},
    {"name":"ann9@mailinator.com","pwd":"123456"},
    {"name":"ann10@mailinator.com","pwd":"123456"},
    {"name":"ann11@mailinator.com","pwd":"123456"},
    {"name":"ann12@mailinator.com","pwd":"123456"},
    {"name":"ann13@mailinator.com","pwd":"123456"},
    {"name":"ann14@mailinator.com","pwd":"123456"},
    {"name":"ann15@mailinator.com","pwd":"123456"},
    {"name":"ann16@mailinator.com","pwd":"123456"},
    {"name":"ann17@mailinator.com","pwd":"123456"},
    {"name":"ann18@mailinator.com","pwd":"123456"},
    {"name":"ann19@mailinator.com","pwd":"123456"},
    {"name":"ann20@mailinator.com","pwd":"123456"},
    {"name":"ann21@mailinator.com","pwd":"123456"},
    {"name":"ann22@mailinator.com","pwd":"123456"},
    {"name":"ann23@mailinator.com","pwd":"123456"},
    {"name":"ann24@mailinator.com","pwd":"123456"},
    {"name":"ann25@mailinator.com","pwd":"123456"},
    {"name":"ann26@mailinator.com","pwd":"123456"},
    {"name":"ann27@mailinator.com","pwd":"123456"},
    {"name":"ann28@mailinator.com","pwd":"123456"},
    {"name":"ann29@mailinator.com","pwd":"123456"},
    {"name":"ann30@mailinator.com","pwd":"123456"},
    {"name":"ann31@mailinator.com","pwd":"123456"},
    {"name":"ann32@mailinator.com","pwd":"123456"},
    {"name":"ann33@mailinator.com","pwd":"123456"},
    {"name":"ann34@mailinator.com","pwd":"123456"},
    {"name":"ann35@mailinator.com","pwd":"123456"},
    {"name":"bob1@mailinator.com","pwd":"123456"},
    {"name":"bob2@mailinator.com","pwd":"123456"},
    {"name":"bob3@mailinator.com","pwd":"123456"},
    {"name":"bob4@mailinator.com","pwd":"123456"},
    {"name":"bob5@mailinator.com","pwd":"123456"},
    {"name":"bob6@mailinator.com","pwd":"123456"},
    {"name":"bob7@mailinator.com","pwd":"123456"},
    {"name":"bob8@mailinator.com","pwd":"123456"},
    {"name":"bob9@mailinator.com","pwd":"123456"},
    {"name":"bob10@mailinator.com","pwd":"123456"},
    {"name":"bob11@mailinator.com","pwd":"123456"},
    {"name":"bob12@mailinator.com","pwd":"123456"},
    {"name":"bob13@mailinator.com","pwd":"123456"},
    {"name":"bob14@mailinator.com","pwd":"123456"},
    {"name":"bob15@mailinator.com","pwd":"123456"},
    {"name":"bob16@mailinator.com","pwd":"123456"},
    {"name":"bob17@mailinator.com","pwd":"123456"},
    {"name":"bob18@mailinator.com","pwd":"123456"},
    {"name":"bob19@mailinator.com","pwd":"123456"},
    {"name":"bob20@mailinator.com","pwd":"123456"},
    {"name":"bob21@mailinator.com","pwd":"123456"},
    {"name":"bob22@mailinator.com","pwd":"123456"},
    {"name":"bob23@mailinator.com","pwd":"123456"},
    {"name":"bob24@mailinator.com","pwd":"123456"},
    {"name":"bob25@mailinator.com","pwd":"123456"},
    {"name":"bob26@mailinator.com","pwd":"123456"},
    {"name":"bob27@mailinator.com","pwd":"123456"},
    '''


login_users = [
    {"name":"daffy@mailinator.com", "pwd":"daffy123"},
    {"name":"minnie@mailinator.com", "pwd":"minnie"},
    {"name":"elmer@mailinator.com", "pwd":"elmer123"},
    {"name":"tweety@mailinator.com", "pwd":"tweety"},
    {"name":"alfonse@mailinator.com", "pwd":"alfonse"},
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
    {"name": "ann1@mailinator.com", "pwd": "123456"},
    {"name": "ann2@mailinator.com", "pwd": "123456"},
    {"name": "ann3@mailinator.com", "pwd": "123456"},
    {"name": "ann4@mailinator.com", "pwd": "123456"},
    {"name": "ann5@mailinator.com", "pwd": "123456"},
    {"name": "ann6@mailinator.com", "pwd": "123456"},
    {"name": "ann7@mailinator.com", "pwd": "123456"},
    {"name": "ann8@mailinator.com", "pwd": "123456"},
    {"name": "ann9@mailinator.com", "pwd": "123456"},
    {"name": "ann10@mailinator.com", "pwd": "123456"},
    {"name": "ann11@mailinator.com", "pwd": "123456"},
    {"name": "ann12@mailinator.com", "pwd": "123456"},
    {"name": "ann13@mailinator.com", "pwd": "123456"},
    {"name": "ann14@mailinator.com", "pwd": "123456"},
    {"name": "ann15@mailinator.com", "pwd": "123456"},
    {"name": "ann16@mailinator.com", "pwd": "123456"},
    {"name": "ann17@mailinator.com", "pwd": "123456"},
    {"name": "ann18@mailinator.com", "pwd": "123456"},
    {"name": "ann19@mailinator.com", "pwd": "123456"},
    {"name": "ann20@mailinator.com", "pwd": "123456"},
    {"name": "ann21@mailinator.com", "pwd": "123456"},
    {"name": "ann22@mailinator.com", "pwd": "123456"},
    {"name": "ann23@mailinator.com", "pwd": "123456"},
    {"name": "ann24@mailinator.com", "pwd": "123456"},
    {"name": "ann25@mailinator.com", "pwd": "123456"},
    {"name": "ann26@mailinator.com", "pwd": "123456"},
    {"name": "ann27@mailinator.com", "pwd": "123456"},
    {"name": "ann28@mailinator.com", "pwd": "123456"},
    {"name": "ann29@mailinator.com", "pwd": "123456"},
    {"name": "ann30@mailinator.com", "pwd": "123456"},
    {"name": "ann31@mailinator.com", "pwd": "123456"},
    {"name": "ann32@mailinator.com", "pwd": "123456"},
    {"name": "ann33@mailinator.com", "pwd": "123456"},
    {"name": "ann34@mailinator.com", "pwd": "123456"},
    {"name": "ann35@mailinator.com", "pwd": "123456"},
    {"name": "bob1@mailinator.com", "pwd": "123456"},
    {"name": "bob2@mailinator.com", "pwd": "123456"},
    {"name": "bob3@mailinator.com", "pwd": "123456"},
    {"name": "bob4@mailinator.com", "pwd": "123456"},
    {"name": "bob5@mailinator.com", "pwd": "123456"},
    {"name": "bob6@mailinator.com", "pwd": "123456"},
    {"name": "bob7@mailinator.com", "pwd": "123456"},
    {"name": "bob8@mailinator.com", "pwd": "123456"},
    {"name": "bob9@mailinator.com", "pwd": "123456"},
    {"name": "bob10@mailinator.com", "pwd": "123456"},
    {"name": "bob11@mailinator.com", "pwd": "123456"},
    {"name": "bob12@mailinator.com", "pwd": "123456"},
    {"name": "bob13@mailinator.com", "pwd": "123456"},
    {"name": "bob14@mailinator.com", "pwd": "123456"},
    {"name": "bob15@mailinator.com", "pwd": "123456"},
    {"name": "bob16@mailinator.com", "pwd": "123456"},
    {"name": "bob17@mailinator.com", "pwd": "123456"},
    {"name": "bob18@mailinator.com", "pwd": "123456"},
    {"name": "bob19@mailinator.com", "pwd": "123456"},
    {"name": "bob20@mailinator.com", "pwd": "123456"},
    {"name": "bob21@mailinator.com", "pwd": "123456"},
    {"name": "bob22@mailinator.com", "pwd": "123456"},
    {"name": "bob23@mailinator.com", "pwd": "123456"},
    {"name": "bob24@mailinator.com", "pwd": "123456"},
    {"name": "bob25@mailinator.com", "pwd": "123456"},
    {"name": "bob26@mailinator.com", "pwd": "123456"},
    {"name": "bob27@mailinator.com", "pwd": "123456"},
]


def get_url(key):
    url = {}
    url["key"] = key
    url["company_base"] = "http://rong.36kr.com/api/company/%s" % key
    url["past_finance"] = "http://rong.36kr.com/api/company/%s/past-finance" % key
    url["past_investor"] = "http://rong.36kr.com/api/company/%s/past-investor?pageSize=100" % key
    url["funds"] = "http://rong.36kr.com/api/company/%s/funds" % key
    url["product"] = "http://rong.36kr.com/api/company/%s/product" % key
    url["past_investment"] = "http://rong.36kr.com/api/company/%s/past-investment" % key
    url["company_fa"] = "http://rong.36kr.com/api/fa/company-fa?cid=%s" % key
    url["founders"] = "http://rong.36kr.com/api/company/%s/founder?pageSize=1000" % key
    url["employees"] = "http://rong.36kr.com/api/company/%s/employee?pageSize=1000" % key
    url["former_members"] = "http://rong.36kr.com/api/company/%s/former-member?pageSize=1000" % key

    return url

class kr36Crawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
            except:
                return False

            if j["msg"].strip() == "您请求的过于频繁，请稍后再试！":
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return False
            else:
                return True
        return False

    def login(self, url, redirect=True):
        while True:
            self.init_http_session(url)

            idx = random.randint(0, len(login_users) - 1)
            login_user = login_users[idx]
            logger.info(login_user)

            data = {
                "type": "login",
                "bind": False,
                "needCaptcha": False,
                "username": login_user["name"],
                "password": login_user["pwd"],
                "ok_url": "/"

            }
            data = urllib.urlencode(data)
            headers = {
                "Referer": "http://passport.36kr.com"
            }
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
            headers['User-Agent'] = user_agent

            try:
                request= urllib2.Request("http://passport.36kr.com/passport/sign_in", data, headers)
                r = self.opener.open(request, timeout=20)
                page=r.read()
                logger.info(page)
            except Exception,e:
                # logger.info(e)
                continue

            if r.getcode() != 200:
                continue

            if page.strip() != '{"countDownTimer":3,"redirect_to":"/"}':
                continue

            try:
                request = urllib2.Request("http://uc.36kr.com/api/user/identity")
                r = self.opener.open(request, timeout=20)
                page = r.read()
                #logger.info(page)
            except:
                continue

            if r.getcode() == 200:
                try:
                    result = json.loads(page)
                except:
                    logger.info(page)
                    continue
                #logger.info(result)
                if result["code"] == 4031:
                    break


def has_content(content):
    if content is not None:
        try:
            j = json.loads(content)
        except:
            logger.info("Not json content")
            logger.info(content)
            return False

        if j["code"] == 0:
            return True
        else:
            logger.info("code=%d, %s" % (j["code"], j["msg"]))
    else:
        logger.info("Fail to get content")

    return False


def process(g, crawler, url, key, content):
    if has_content(content):

        company={}
        company_base = json.loads(content)
        company["company_base"] = company_base
        logger.info(company_base["data"]["company"]["name"])
        url_map = get_url(key)
        for k in url_map.keys():
            if k != "key" and k != "company_base":
                result = crawler.crawl(url_map[k])
                while True:
                    if result['get'] == 'success':
                        break
                    elif result["content"] is not None and result["content"].find("后台出错，请联系管理员！") > 0:
                        break
                    else:
                        result = crawler.crawl(url_map[k])
                content_more =result['content']
                if has_content(content_more):
                    company[k] = json.loads(content_more)
                    logger.info(company[k])
                    # time.sleep(random.randint(3,8))

        #t.process(url_map["company_base"], key, company)
        crawler.save(g.SOURCE, g.TYPE, url, key, company)
        g.latestIncr()


def crawl(crawler, key, g):
    url = "http://rong.36kr.com/api/company/%s" % key
    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            #logger.info(result["content"])
            try:
                process(g, crawler, url, key, result['content'])
            except Exception,ex:
                logger.exception(ex)
            break


def run(g, crawler, flag):
    while True:
        num = 100
        if flag == "all":
            num = 300
        if g.finish(num=num):
            return
        key = g.nextKey()
        crawl(crawler, key, g)


def start_run(concurrent_num, flag):
    while True:
        logger.info("36kr company %s start...", flag)

        g = GlobalValues.GlobalValues(13020, 36001, flag, back=1)

        threads = [gevent.spawn(run, g, kr36Crawler(),flag) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("36kr company %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*30)        #30 minutes
        else:
            gevent.sleep(60*60)   #12hour

        #break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(1, "all")
        else:
            key = str(int(param))
            g = GlobalValues.GlobalValues(13020, 36001, "incr", back=0)
            crawl(kr36Crawler(), key, g)
    else:
        start_run(1, "incr")