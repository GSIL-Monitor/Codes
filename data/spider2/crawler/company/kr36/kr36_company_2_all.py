# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, random
from lxml import html
from pyquery import PyQuery as pq
import urllib2
import urllib
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
import loghelper,db

#logger
loghelper.init_logger("crawler_36kr_company2", stream=True)
logger = loghelper.get_logger("crawler_36kr_company2")

TYPE = 36001
SOURCE =13022
URLS = []
CURRENT_PAGE = 1
linkPattern = "/article/\d+"
Nocontents = [
]

columns0 = [
    {"column": None, "max": 3},
    {"column": "FARMING", "max": 3},{"column": "E_COMMERCE", "max": 3},{"column": "SOCIAL_NETWORK", "max": 3},
    {"column": "INTELLIGENT_HARDWARE", "max": 3},{"column": "MEDIA", "max": 3},{"column": "SOFTWARE", "max": 3},
    {"column": "CONSUMER_LIFESTYLE", "max": 3},{"column": "FINANCE", "max": 3},{"column": "MEDICAL_HEALTH", "max": 3},
    {"column": "SERVICE_INDUSTRIES", "max": 3},{"column": "TRAVEL_OUTDOORS", "max": 3},{"column": "PROPERTY_AND_HOME_FURNISHINGS", "max": 3},
    {"column": "EDUCATION_TRAINING", "max": 3}, {"column": "AUTO", "max": 3}, {"column": "LOGISTICS", "max": 3},
    {"column": "AI", "max": 3}, {"column": "UAV", "max": 3}, {"column": "ROBOT", "max": 3},
    {"column": "VR_AR", "max": 3}, {"column": "SPORTS", "max": 3}, {"column": "SHARE_BUSINESS", "max": 3},
    {"column": "CHU_HAI", "max": 3}, {"column": "CONSUME", "max": 3},
]


columns = [
           {"id":25,"cnt":1903,"name":"大数据"},
           {"id":187,"cnt":1814,"name":"影视"},{"id":572,"cnt":1445,"name":"SaaS"},{"id":834,"cnt":1301,"name":"职业培训"},{"id":165,"cnt":1010,"name":"K12"},{"id":200,"cnt":1005,"name":"安全服务"},{"id":185,"cnt":958,"name":"智能家居"},{"id":589,"cnt":935,"name":"云计算"},{"id":248,"cnt":777,"name":"直播"},{"id":96,"cnt":707,"name":"自媒体"},{"id":688,"cnt":695,"name":"健身"},{"id":17,"cnt":682,"name":"原创IP"},{"id":197,"cnt":676,"name":"艺人网红"},{"id":91,"cnt":664,"name":"音乐"},{"id":125,"cnt":634,"name":"医疗信息化"},{"id":416,"cnt":624,"name":"精准营销"},{"id":64,"cnt":617,"name":"语言学习"},{"id":142,"cnt":592,"name":"二次元"},{"id":99,"cnt":544,"name":"可穿戴设备"},{"id":151,"cnt":538,"name":"留学服务"},{"id":182,"cnt":505,"name":"户外/极限"},{"id":788,"cnt":454,"name":"赛事"},{"id":473,"cnt":400,"name":"学前教育"},{"id":124,"cnt":369,"name":"农业电商"},{"id":155,"cnt":360,"name":"医疗器械"},{"id":127,"cnt":343,"name":"供应链金融"},{"id":675,"cnt":332,"name":"计算机视觉"},{"id":760,"cnt":329,"name":"短视频"},{"id":639,"cnt":279,"name":"运动社区"},{"id":9,"cnt":265,"name":"消费品"},{"id":110,"cnt":244,"name":"大数据征信"},{"id":245,"cnt":229,"name":"AR"},{"id":797,"cnt":220,"name":"足球"},{"id":270,"cnt":218,"name":"基因检测"},{"id":135,"cnt":204,"name":"FinTech"},{"id":159,"cnt":199,"name":"消费金融"},{"id":841,"cnt":181,"name":"医疗影像"},{"id":673,"cnt":178,"name":"VR硬件"},{"id":791,"cnt":176,"name":"运动场馆"},{"id":525,"cnt":169,"name":"VR游戏"},{"id":835,"cnt":165,"name":"智能教学"},{"id":65,"cnt":159,"name":"区块链"},{"id":706,"cnt":159,"name":"大数据风控"},{"id":745,"cnt":153,"name":"电竞"},{"id":391,"cnt":132,"name":"互联网保险"},{"id":573,"cnt":131,"name":"自然语言处理"},{"id":761,"cnt":130,"name":"衍生品"},{"id":584,"cnt":118,"name":"汽车金融"},{"id":279,"cnt":118,"name":"考研国考"},{"id":824,"cnt":93,"name":"量化交易"},{"id":722,"cnt":85,"name":"工业机器人"},{"id":737,"cnt":83,"name":"VR技术"},{"id":723,"cnt":83,"name":"服务型机器人"},{"id":842,"cnt":82,"name":"药品零售"},{"id":798,"cnt":79,"name":"篮球"},{"id":800,"cnt":72,"name":"体育培训"},{"id":513,"cnt":68,"name":"深度学习"},{"id":794,"cnt":67,"name":"体育用品"},{"id":825,"cnt":67,"name":"海外投资"},{"id":837,"cnt":63,"name":"连锁专科"},{"id":726,"cnt":62,"name":"家用机器人"},{"id":812,"cnt":62,"name":"智慧农业"},{"id":840,"cnt":59,"name":"体外诊断"},{"id":743,"cnt":55,"name":"智能医疗设备"},{"id":705,"cnt":54,"name":"智能投顾"},{"id":829,"cnt":51,"name":"最后一公里"},{"id":694,"cnt":50,"name":"传感器及中间件"},{"id":710,"cnt":47,"name":"无人机技术"},{"id":249,"cnt":46,"name":"自动驾驶"},{"id":701,"cnt":42,"name":"AI安防"},{"id":708,"cnt":41,"name":"工业级无人机"},{"id":709,"cnt":35,"name":"消费级无人机"},{"id":303,"cnt":33,"name":"VR平台/工具"},{"id":700,"cnt":32,"name":"智能诊断"},{"id":839,"cnt":30,"name":"康复机构"},{"id":828,"cnt":27,"name":"智能仓储"},{"id":698,"cnt":26,"name":"AI医疗"},{"id":796,"cnt":24,"name":"体育大数据"},{"id":697,"cnt":19,"name":"AI芯片"},{"id":729,"cnt":17,"name":"机器人算法"},{"id":704,"cnt":16,"name":"AI金融"},{"id":817,"cnt":12,"name":"农村小额信贷"},{"id":816,"cnt":12,"name":"无人机植保"},{"id":420,"cnt":8,"name":"PaaS"},{"id":731,"cnt":8,"name":"VR医疗"},{"id":831,"cnt":8,"name":"自动搬运机器人"},{"id":595,"cnt":6,"name":"IaaS"},{"id":707,"cnt":3,"name":"AI教育"},{"id":830,"cnt":2,"name":"物流分拣"},{"id":114,"cnt":1,"name":"兴趣教育"},{"id":79,"cnt":1,"name":"智能出行"}]

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

            if j["msg"].strip() == "操作成功！":
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


def run_news(column, crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["id"], URL["name"])

def crawler_news(column, crawler, id, name):

    company = {}
    logger.info("start crawler %s|%s", id, name)
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
    if item is not None:
        if item["content"] != content:
            collection.delete_one({"source": SOURCE, "type": TYPE, "key": key})
            logger.info("old data changed for company: %s", key)
        else:
            logger.info("old data not changed for company: %s", key)
            newflag = False
    if newflag is True: collection.insert_one(collection_content)
    mongo.close()
    logger.info("Saved: %s", url)


def process(content, flag):

    j = json.loads(content)
    # logger.info(content)
    companies = j["data"]["pageData"]["data"]

    cnt = 0
    if len(companies) == 0:
        return cnt, cnt

    for a in companies:
        try:

            id = a["id"]
            name = a["name"]
            logger.info("company: %s|%s", id, name)

            # check mongo data if link is existed
            mongo = db.connect_mongo()
            collection_news = mongo.raw.projectdata
            item = collection_news.find_one({"source": SOURCE, "key_int": int(id)})
            mongo.close()
            if item is None:
                URLS.append(a)
        except Exception, e:
            logger.info(e)
            logger.info("cannot get company data")
    return len(companies), len(URLS)

def run(flag, column0, column, listcrawler, companycrawler, concurrent_num):
    global CURRENT_PAGE
    cnt = 20
    logger.info("crawler label %s",column["name"])
    while True:
        key = CURRENT_PAGE

        if flag == "all":
            if key > 50:
                return
        else:
            if cnt < 20 or key > 50:
                return

        CURRENT_PAGE += 1
        if column0["column"] is None:
            url = 'https://rong.36kr.com/n/api/column/0/company?label=%s&sortField=HOT_SCORE&p=%s' \
                  % (column["id"], key)
        else:
            url = 'https://rong.36kr.com/n/api/column/0/company?industry=%s&label=%s&sortField=HOT_SCORE&p=%s' \
              % (column0["column"], column["id"], key)

        while True:
            result = listcrawler.crawl(url,agent=True)

            if result['get'] == 'success':
                try:
                    cnt, cnt2 = process(result['content'], flag)
                    if cnt2 > 0:
                        logger.info("%s has %s/%s fresh company", url, cnt2, cnt)
                        logger.info(URLS)
                        threads = [gevent.spawn(run_news, column, companycrawler) for i in xrange(concurrent_num)]
                        gevent.joinall(threads)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 20
                break



def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s company all %s start...", SOURCE, flag)
        listcrawler = kr36Crawler()
        companycrawler = kr36Crawler()

        # download_crawler = None
        for column0 in columns0:
            for column in columns:
                CURRENT_PAGE = 1

                run(flag, column0, column, listcrawler, companycrawler, concurrent_num)
                # break

        if flag == "incr":
            gevent.sleep(60*60)        #30 minutes
        else:
            return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(1, "all")
        else:
            link = param
            crawler_news({},kr36Crawler(),link, "aaaaaa")

    else:
        start_run(1, "incr")