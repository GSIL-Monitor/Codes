# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, random
from lxml import html
from pyquery import PyQuery as pq
import urllib2
import urllib
import time
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
from urllib import quote

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db

import kr36_user
#logger
loghelper.init_logger("crawler_36kr_company2_search", stream=True)
logger = loghelper.get_logger("crawler_36kr_company2_search")

TYPE = 36001
SOURCE =13022
# URLS = []
KEYCS = []
CURRENT_PAGE = 1
linkPattern = "/article/\d+"
Nocontents = [
]

# companycrawler = kr36Crawler()

# login_users = [
#
#     {"name": "hgb@mailinator.com", "pwd": "123456"},
#     {"name": "zhaoyi@mailinator.com", "pwd": "123456"},
#     {"name": "yizhao@mailinator.com", "pwd": "123456"},
#     {"name": "yi_29@mailinator.com", "pwd": "123456"},
#     {"name": "ss_zhaoyi@mailinator.com", "pwd": "123456"},
#     {"name": "jiaoda_zhao@mailinator.com", "pwd": "123456"},
#     {"name": "minghang_zhao@mailinator.com", "pwd": "123456"},
#     {"name": "jiyang_yi@mailinator.com", "pwd": "123456"},
#     {"name": "boyika_29@mailinator.com", "pwd": "123456"},
#     {"name": "29_marrr@mailinator.com", "pwd": "123456"},
#     {"name": "jiangxi_ss@mailinator.com", "pwd": "123456"},
#     {"name": "ty_zhao@mailinator.com", "pwd": "123456"},
#     {"name": "yizhao23ide@mailinator.com", "pwd": "123456"},
#     {"name": "nena_yz@mailinator.com", "pwd": "123456"},
#     {"name": "zzy_zhao@mailinator.com", "pwd": "123456"},
#     {"name": "xy_yz@mailinator.com", "pwd": "123456"},
#     {"name": "sjsu_@mailinator.com", "pwd": "123456"},
#     {"name": "daytime_zhao@mailinator.com", "pwd": "123456"},
#     {"name": "wede_z@mailinator.com", "pwd": "123456"},
#     {"name": "fc_yz@mailinator.com", "pwd": "123456"},
#
#     {"name": "shkjSeeStory@mailinator.com", "pwd": "123456"},
#     {"name": "dasouche@mailinator.com", "pwd": "123456"},
#     {"name": "bjshjmdj@mailinator.com", "pwd": "123456"},
#     {"name": "dingxiangyuan@mailinator.com", "pwd": "123456"},
#     {"name": "8Securities@mailinator.com", "pwd": "123456"},
#     {"name": "lingdongxincheng@mailinator.com", "pwd": "123456"},
#     {"name": "beijingdianfengkeji@mailinator.com", "pwd": "123456"},
#     {"name": "guangzhoubozhao@mailinator.com", "pwd": "123456"},
#     {"name": "ruituokeji@mailinator.com", "pwd": "123456"},
#     {"name": "jianguoG1@mailinator.com", "pwd": "123456"},
#     {"name": "zhanglingwuxian@mailinator.com", "pwd": "123456"},
#     {"name": "mogubang@mailinator.com", "pwd": "123456"},
#     {"name": "EasyStackjsd@mailinator.com", "pwd": "123456"},
#     {"name": "Mercari@mailinator.com", "pwd": "123456"},
#     {"name": "pinganjiankang@mailinator.com", "pwd": "123456"},
#     {"name": "Hired@mailinator.com", "pwd": "123456"},
#     {"name": "Birchbox@mailinator.com", "pwd": "123456"},
#     {"name": "GeneralAssembly@mailinator.com", "pwd": "123456"},
#     {"name": "StoreDot@mailinator.com", "pwd": "123456"},
#     {"name": "DocuSign@mailinator.com", "pwd": "123456"},
#
# ]

def get_url(key):
    millis = int(round(time.time() * 1000))
    url = {}
    url["key"] = key
    url["company_base"] = "https://rong.36kr.com/n/api/company/%s?asEncryptedTs=0.2865982147907245&asTs=%s" % (key,millis)
    url["past_finance"] = "https://rong.36kr.com/n/api/company/%s/finance?asEncryptedTs=0.2865982147907245&asTs=%s" % (key,millis)
    # url["past_investor"] = "http://rong.36kr.com/api/company/%s/past-investor?pageSize=100" % key
    # url["funds"] = "https://rong.36kr.com/n/api/company/%s/funds" % key
    url["product"] = "https://rong.36kr.com/n/api/company/%s/product?asEncryptedTs=0.2865982147907245&asTs=%s" % (key,millis)
    # url["past_investment"] = "http://rong.36kr.com/api/company/%s/past-investment" % key
    # url["company_fa"] = "http://rong.36kr.com/api/fa/company-fa?cid=%s" % key
    # url["founders"] = "http://rong.36kr.com/api/company/%s/founder?pageSize=1000" % key
    # url["employees"] = "http://rong.36kr.com/api/company/%s/employee?pageSize=1000" % key
    # url["former_members"] = "http://rong.36kr.com/api/company/%s/former-member?pageSize=1000" % key
    url["member"] = "https://rong.36kr.com/n/api/company/%s/member?asEncryptedTs=0.2865982147907245&asTs=%s" % (key,millis)
    # url["similar"] = "https://rong.36kr.com/n/api/company/%s/similar" % key

    return url


# class ListCrawler(BaseCrawler.BaseCrawler):
#     def __init__(self, timeout=33):
#         BaseCrawler.BaseCrawler.__init__(self,timeout=timeout)
#
#     def is_crawl_success(self, url, content):
#         if content is not None:
#             try:
#                 j = json.loads(content)
#             except:
#                 return False
#
#             if j["msg"].strip() == "操作成功！" or j["msg"].strip() == "公司不存在":
#                 logger.info("code=%d, %s" % (j["code"], j["msg"]))
#                 return True
#             else:
#                 logger.info("code=%d, %s" % (j["code"], j["msg"]))
#                 return False
#         return False
#
#     def login(self, url, redirect=True):
#         while True:
#             self.init_http_session(url)
#
#             idx = random.randint(0, len(login_users) - 1)
#             login_user = login_users[idx]
#             logger.info(login_user)
#             logger.info("want: %s", url)
#
#             data = {
#                 "type": "login",
#                 "bind": False,
#                 "needCaptcha": False,
#                 "username": login_user["name"],
#                 "password": login_user["pwd"],
#                 "ok_url": "/"
#
#             }
#             data = urllib.urlencode(data)
#             headers = {
#                 "Referer": "https://passport.36kr.com"
#             }
#             user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
#             headers['User-Agent'] = user_agent
#
#             try:
#                 request = urllib2.Request("https://passport.36kr.com/passport/sign_in", data, headers)
#                 r = self.opener.open(request, timeout=30)
#                 page = r.read()
#                 logger.info(page)
#             except Exception, e:
#                 logger.info("wrong 1")
#                 logger.info(e)
#                 continue
#
#             if r.getcode() != 200:
#                 logger.info("wrong 2")
#                 continue
#
#             if page.strip() != '{"countDownTimer":3,"redirect_to":"/"}':
#                 logger.info("wrong 3")
#                 continue
#
#             try:
#                 request = urllib2.Request("https://uc.36kr.com/api/user/identity")
#                 r = self.opener.open(request, timeout=30)
#                 page = r.read()
#                 logger.info("identity")
#                 logger.info(page)
#             except:
#                 logger.info("wrong here")
#                 continue
#
#             if r.getcode() == 200:
#                 try:
#                     result = json.loads(page)
#                 except:
#                     logger.info("wrong 4")
#                     logger.info(page)
#
#                     continue
#                 # logger.info(result)
#                 if result["code"] == 0 and result["msg"] == "操作成功！":
#                     break
#             else:
#                 logger.info("wrong 5, %s", r.getcode())
#
#
# class kr36Crawler(BaseCrawler.BaseCrawler):
#     def __init__(self,timeout=33,max_crawl=20):
#         BaseCrawler.BaseCrawler.__init__(self,timeout=timeout,max_crawl=max_crawl)
#
#     def is_crawl_success(self, url, content):
#         if content is not None:
#             try:
#                 j = json.loads(content)
#             except:
#                 return False
#
#             if j["msg"].strip() == "操作成功！"  or j["msg"].strip() == "公司不存在":
#                 logger.info("code=%d, %s" % (j["code"], j["msg"]))
#                 return True
#             else:
#                 logger.info("code=%d, %s" % (j["code"], j["msg"]))
#                 return False
#         return False
#
#     def login(self, url, redirect=True):
#         while True:
#             self.init_http_session(url)
#
#             idx = random.randint(0, len(login_users) - 1)
#             login_user = login_users[idx]
#             logger.info(login_user)
#             logger.info("want: %s", url)
#
#             data = {
#                 "type": "login",
#                 "bind": False,
#                 "needCaptcha": False,
#                 "username": login_user["name"],
#                 "password": login_user["pwd"],
#                 "ok_url": "/"
#
#             }
#             data = urllib.urlencode(data)
#             headers = {
#                 "Referer": "https://passport.36kr.com"
#             }
#             user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
#             headers['User-Agent'] = user_agent
#
#             try:
#                 request= urllib2.Request("https://passport.36kr.com/passport/sign_in", data, headers)
#                 r = self.opener.open(request, timeout=30)
#                 page=r.read()
#                 logger.info(page)
#             except Exception,e:
#                 logger.info("wrong 1")
#                 logger.info(e)
#                 continue
#
#             if r.getcode() != 200:
#                 logger.info("wrong 2")
#                 continue
#
#             if page.strip() != '{"countDownTimer":3,"redirect_to":"/"}':
#                 logger.info("wrong 3")
#                 continue
#
#             try:
#                 request = urllib2.Request("https://uc.36kr.com/api/user/identity")
#                 r = self.opener.open(request, timeout=30)
#                 page = r.read()
#                 logger.info("identity")
#                 logger.info(page)
#             except:
#                 logger.info("wrong here")
#                 continue
#
#             if r.getcode() == 200:
#                 try:
#                     result = json.loads(page)
#                 except:
#                     logger.info("wrong 4")
#                     logger.info(page)
#
#                     continue
#                 #logger.info(result)
#                 if result["code"] == 0 and result["msg"] == "操作成功！":
#                     break
#             else:
#                 logger.info("wrong 5, %s",r.getcode())

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


def run_news(column, crawler, URL):

    logger.info(URL)
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
        time.sleep(3)
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
        "key": int(key),
        "key_int": key_int,
        "content": content
    }
    newflag = True
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    item = collection.find_one({"source": SOURCE, "type": TYPE, "key": int(key)})
    if item is not None:
        if item["content"] != content:
            collection.delete_one({"source": SOURCE, "type": TYPE, "key": int(key)})
            logger.info("old data changed for company: %s", key)
        else:
            logger.info("old data not changed for company: %s", key)
            newflag = False
    if newflag is True: collection.insert_one(collection_content)
    mongo.close()
    logger.info("Saved: %s", url)


def process(content, flag, column):

    j = json.loads(content)
    # logger.info(content)

    companies = j["data"]["pageData"]["data"]
    urls = []
    cnt = 0
    if len(companies) == 0:
        return urls

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
            if item is None or ((datetime.datetime.now() - item["date"]).days>= 1):
            # if item is None:
                urls.append(a)
        except Exception, e:
            logger.info(e)
            logger.info("cannot get company data")
    return urls

def run_search(flag, column, listcrawler, companycrawler, concurrent_num, keyword):
    millis = int(round(time.time() * 1000))
    # url = 'https://rong.36kr.com/n/api/search/company?kw=%s&sortField=MATCH_RATE' % keyword
    url = 'https://rong.36kr.com/n/api/search/company?asEncryptedTs=-0.8477744763834107&asTs=%s&kw=%s&sortField=MATCH_RATE' % (millis, quote(keyword.encode('utf-8')))
    retry = 0
    while True:
        result = listcrawler.crawl(url,agent=True)

        if result['get'] == 'success':
            try:
                URLS = process(result['content'], flag, column)
                if len(URLS) > 0:
                    logger.info("%s has %s fresh company", url, len(URLS))
                    logger.info(URLS)
                    time.sleep(random.randint(13, 18))
                    # threads = [gevent.spawn(run_news, column, companycrawler) for i in xrange(concurrent_num)]
                    # gevent.joinall(threads)
                    for URL in URLS:
                        run_news(column, companycrawler, URL)
                        time.sleep(random.randint(13, 18))
                    # exit()
            except Exception,ex:
                logger.exception(ex)
                cnt = 0
            break
        if retry > 20:
            break
        retry += 1
        time.sleep(random.randint(1,10))



def ss_run(listcrawler,companycrawler):

    while True:

        if len(KEYCS) == 0:
            return
        KEYC = KEYCS.pop(0)
        keyword = KEYC["keyword"]
        sourceId = KEYC["sourceId"]
        logger.info("*******here kr36 search %s|%s", keyword, sourceId)
        if sourceId is None:
            run_search("incr",{},listcrawler,companycrawler,1, keyword)
        else:
            crawler_news({}, companycrawler, str(sourceId), "new")
        # break

def start_run(kcolumns):
    ccrawler = kr36_user.ListCrawler()
    for k in kcolumns:
        KEYCS.append(k)
    if len(KEYCS) > 0:
        # threads = [gevent.spawn(ss_run, ListCrawler(), kr36Crawler()) for i in xrange(3)]
        # gevent.joinall(threads)
        threads = [gevent.spawn(ss_run, ccrawler, ccrawler) for i in xrange(1)]
        gevent.joinall(threads)


    # global CURRENT_PAGE
    # while True:
    #     logger.info("%s company %s start...", SOURCE, flag)
    #     listcrawler = ListCrawler()
    #     companycrawler = kr36Crawler()
    #
    #     # download_crawler = None
    #     for column in columns:
    #         CURRENT_PAGE = 1
    #         run(flag, column, listcrawler, companycrawler, concurrent_num)
    #
    #     if flag == "incr":
    #         gevent.sleep(60*60)        #30 minutes
    #     else:
    #         return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":

    start_run("teambition", None, ListCrawler(), kr36Crawler())