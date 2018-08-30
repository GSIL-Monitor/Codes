# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, random, time
from lxml import html
from pyquery import PyQuery as pq
import urllib2
import urllib


reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db

#logger
loghelper.init_logger("crawler_36kr_company3", stream=True)
logger = loghelper.get_logger("crawler_36kr_company3")

TYPE = 36001
SOURCE =13022
URLS = []
CURRENT_PAGE = 1
DATE = None
Nocontents = [
]


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
    url["company_base"] = "https://rong.36kr.com/n/api/company/%s" % key
    url["past_finance"] = "https://rong.36kr.com/n/api/company/%s/finance" % key
    # url["past_investor"] = "http://rong.36kr.com/api/company/%s/past-investor?pageSize=100" % key
    # url["funds"] = "https://rong.36kr.com/n/api/company/%s/funds" % key
    url["product"] = "https://rong.36kr.com/n/api/company/%s/product" % key
    # url["past_investment"] = "http://rong.36kr.com/api/company/%s/past-investment" % key
    # url["company_fa"] = "http://rong.36kr.com/api/fa/company-fa?cid=%s" % key
    # url["founders"] = "http://rong.36kr.com/api/company/%s/founder?pageSize=1000" % key
    # url["employees"] = "http://rong.36kr.com/api/company/%s/employee?pageSize=1000" % key
    # url["former_members"] = "http://rong.36kr.com/api/company/%s/former-member?pageSize=1000" % key
    url["member"] = "https://rong.36kr.com/n/api/company/%s/member" % key
    url["similar"] = "https://rong.36kr.com/n/api/company/%s/similar" % key

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

            if j["msg"].strip() == "操作成功！" or j["msg"].strip() == "公司不存在":
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return True
            else:
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return False
        return False

    def login(self, url, redirect=True):
        while True:
            self.init_http_session(url)

            idx = random.randint(0, len(login_users) - 1)
            login_user = login_users[idx]
            logger.info(login_user)
            logger.info("want: %s", url)

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
                "Referer": "https://passport.36kr.com"
            }
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
            headers['User-Agent'] = user_agent

            try:
                request= urllib2.Request("https://passport.36kr.com/passport/sign_in", data, headers)
                r = self.opener.open(request, timeout=20)
                page=r.read()
                logger.info(page)
            except Exception,e:
                logger.info("wrong 1")
                logger.info(e)
                continue

            if r.getcode() != 200:
                logger.info("wrong 2")
                continue

            if page.strip() != '{"countDownTimer":3,"redirect_to":"/"}':
                logger.info("wrong 3")
                continue

            try:
                request = urllib2.Request("https://uc.36kr.com/api/user/identity")
                r = self.opener.open(request, timeout=20)
                page = r.read()
                logger.info("identity")
                logger.info(page)
            except:
                logger.info("wrong here")
                continue

            if r.getcode() == 200:
                try:
                    result = json.loads(page)
                except:
                    logger.info("wrong 4")
                    logger.info(page)

                    continue
                #logger.info(result)
                if result["code"] == 0 and result["msg"] == "操作成功！":
                    break
            else:
                logger.info("wrong 5, %s",r.getcode())


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


def run_news(crawler):
    while True:
        if len(URLS) == 0:
            return
        id = URLS.pop(0)

        crawler_news(crawler, id)

def crawler_news(crawler, id):

    company = {}
    logger.info("start crawler %s", id)
    url_map = get_url(id)
    for k in url_map.keys():
        if k != "key":
            result = crawler.crawl(url_map[k])
            while True:
                if result['get'] == 'success':
                    break
                elif result["content"] is not None and result["content"].find("后台出错，请联系管理员！") > 0:
                    break
                else:
                    result = crawler.crawl(url_map[k])
            content_more = result['content']
            if has_content(content_more):
                company[k] = json.loads(content_more)
                logger.info(company[k])
                # time.sleep(random.randint(3,8))

    save(SOURCE, TYPE, url_map["company_base"], id, company)


def save(SOURCE, TYPE, url, key, content):
    global CURRENT_PAGE
    logger.info("Saving: %s", url)
    try:
        key_int = int(key)
    except:
        key_int = None

    collection_content = {
        "date": datetime.datetime.now(),
        "source": SOURCE,
        "type": TYPE,
        "url": url,
        "key": key,
        "key_int": key_int,
        "content": content
    }
    newflag = True
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    item = collection.find_one({"source": SOURCE, "type": TYPE, "key": key})
    # if item is not None:
    #     if item["content"] != content:
    #         collection.delete_one({"source": SOURCE, "type": TYPE, "key": key})
    #         logger.info("old data changed for company: %s", key)
    #     else:
    #         logger.info("old data not changed for company: %s", key)
    #         newflag = False
    # if newflag is True: collection.insert_one(collection_content)
    if item is None:
        collection.insert_one(collection_content)
        CURRENT_PAGE += 1
    mongo.close()
    logger.info("Saved: %s", url)


def process():
    mongo = db.connect_mongo()
    collection_news = mongo.raw.projectdata
    items = list(collection_news.find({"source": SOURCE, "type":TYPE, "sChecked": None}, limit=10))


    for a in items:
        try:
            simliars = a["content"]["similar"]["data"]
            for similar in simliars:
                cls = similar["companyList"]
                for cl in cls:
                    id = cl["id"]
                    name = cl["name"]
                    # logger.info("company: %s|%s", id, name)

                    # check mongo data if link is existed
                    if int(id) in URLS:
                        continue

                    item = collection_news.find_one({"source": SOURCE, "type":TYPE, "key_int": int(id)})
                    if item is None:
                        logger.info("company: %s|%s   not found", id, name)
                        URLS.append(int(id))
        except Exception, e:
            logger.info(e)
            logger.info("cannot get company data")

        collection_news.update_one({"_id": a["_id"]}, {'$set': {"sChecked": True}})

    mongo.close()


    return len(items), len(URLS)

def run(flag,listcrawler, companycrawler, concurrent_num):
    global CURRENT_PAGE
    while True:
        try:
            cnt, cnt2 = process()
            logger.info("%s - %s", cnt, cnt2)
            if cnt2 > 0:
                logger.info("similar check has %s/%s fresh company", cnt2, cnt)
                run_news(companycrawler)

        except Exception, E:
            logger.info(E)
            pass

        if CURRENT_PAGE > 40:
            logger.info("exceed 200 stop for next day ok guys?")
            break




def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    global DATE
    while True:
        dt = datetime.date.today()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        if datestr != DATE:
            CURRENT_PAGE = 0
            DATE = datestr
            logger.info("%s company all similar %s start...", SOURCE, flag)
            listcrawler = kr36Crawler()
            companycrawler = kr36Crawler()


            run(flag, listcrawler, companycrawler, concurrent_num)

        time.sleep(60*60)

if __name__ == "__main__":

    start_run(1, "incr")