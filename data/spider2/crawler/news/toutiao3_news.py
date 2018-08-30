# -*- coding: utf-8 -*-
import os, sys,datetime, time
import random, math
import urllib
import os, sys, datetime, re, json
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
import platform
import time,re,cStringIO,urllib2,random
from pyvirtualdisplay import Display
import StringIO


reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../news'))
import Wechatcrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool


#logger
loghelper.init_logger("sogou_news", stream=True)
logger = loghelper.get_logger("sogou_news")


columns = [
    {"url":"https://www.toutiao.com/c/user/6347006294/#mid=6350075797",
     "keyword": "创投分析"}

]

def get_proxy():
    proxy = {"$or": [{'type': 'socks4'}, {'type': 'socks5'}], 'anonymity': 'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            logger.info("No proxy !!!!!!!!!!!!!!!!!!!")
            time.sleep(30)
    return proxy_ip


def is_crawl_success(content, keyword):
    if content.find("</html>") == -1:
        return False
    d = pq(html.fromstring(content.decode("utf-8")))
    logger.info(content)
    title = d('head> title').text().strip()
    if title.find("搜狗微信搜索") >= 0 and title.find(keyword)>=0:
        logger.info("COOOOOOOOOOOOOOR")
        return True
    return False

class wechat(Wechatcrawler.NewsDownloader):
    def __init__(self, TYPE=60005, SOURCE=13847, RETRY=20):
        Wechatcrawler.NewsDownloader.__init__(self, TYPE = TYPE, SOURCE=SOURCE, RETRY=RETRY)



def get():

    for column in columns:
        link = column["url"]
        keyword = column["keyword"]
        cnt = get_article_links(keyword, link)
        #     if cnt>0:
        #         time.sleep(3*60)
        #     else:
        #         time.sleep(1*60)
        # time.sleep(5*60)

def get_article_links(keyword,nr_link):
    cnt1 = 0
    while True:
        driver = None
        try:
            socks = get_proxy()
            # dcap = dict(DesiredCapabilities.PHANTOMJS)
            # dcap["phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36';
            # # dcap["phantomjs.page.settings.loadImages"] = False
            # proxy = '--proxy='+str(socks["ip"]) + ":" + str(socks["port"])
            # if socks["http_type"].lower() == "socks4":
            #     ptype = '--proxy-type=socks4'
            # else:
            #     ptype = '--proxy-type=socks5'
            # # service_args = [proxy, ptype]
            # service_args = []
            # service_args.append('--load-images=no')  ##关闭图片加载
            # service_args.append('--disk-cache=yes')  ##开启缓存
            # service_args.append('--ignore-ssl-errors=true')  ##忽略https错误
            # logger.info(proxy)
            # driver = webdriver.PhantomJS('/opt/phantomjs/bin/phantomjs',
            #                              desired_capabilities=dcap, service_args=service_args)
            headers = {}
            headers["User-Agent"] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
            system = platform.system()
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("user-agent=" + headers["User-Agent"])
            # if ip_port:
            #     chrome_options.add_argument('--proxy-server=%s' % ip_port)
            if system == "Darwin":
                driver = webdriver.Chrome("/data/task-201606/geetest/chromedriver-linux", chrome_options=chrome_options)
            elif system == "Linux":
                chrome_options.binary_location = "/opt/google/chrome/google-chrome"
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-setuid-sandbox")
                driver = webdriver.Chrome("/data/task-201606/geetest/chromedriver-linux", chrome_options=chrome_options)
            else:
                print "Wrong system"
                exit()
            logger.info("start get")
            cokies = gen_cookie()
            driver.delete_all_cookies()
            for c in cokies:
                driver.add_cookie({
                    "domain": '.toutiao.com',
                    "name": c,
                    "value": cokies[c],
                    'path': '/', 'expires': None
                })
            # driver.implicitly_wait(20)
            # driver.set_page_load_timeout(20)
            # driver.set_script_timeout(20)
            driver.implicitly_wait(200)
            driver.set_page_load_timeout(20)
            driver.set_script_timeout(20)
            # script = "var page=this;page.onResourceRequested = function (request){page.browserLog.push(request.url);};"
            # driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')
            # driver.execute('executePhantomScript', {'script': script, 'args': []})

            driver.get(nr_link)
            # driver.implicitly_wait(200)
            # driver.set_page_load_timeout(20)
            # driver.set_script_timeout(20)
            # for i in range(2):
            #     # 设置下拉次数模拟下拉滚动条加载网页
            #     driver.execute_script("window.scrollBy(0,700)")
            #     driver.implicitly_wait(5)
            # script = "var page=this;page.onResourceRequested = function (request){page.browserLog.push(request.url);};"
            # driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')
            # driver.execute('executePhantomScript', {'script': script, 'args': []})

            html = driver.page_source
            logger.info(html)
            logger.info(driver.get_log('browser'))
            break
        except Exception, E:
            logger.info(E)
            if driver is not None:
                driver.close()

    return cnt1

def gen_cookie():
    url = "https://www.toutiao.com/c/user/6347006294/#mid=6350075797"
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap[
        "phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    # dcap["phantomjs.page.settings.loadImages"] = False
    # proxy = '--proxy=' + str(socks["ip"]) + ":" + str(socks["port"])
    driver = webdriver.PhantomJS('/opt/phantomjs/bin/phantomjs',
                                 desired_capabilities=dcap)
    driver.get(url)
    raw_cookies = driver.get_cookies()
    driver.quit()
    # display.stop()

    cookies = {}
    for c in raw_cookies:
        cookies[c["name"].encode("utf8")] = c["value"].encode("utf8")
        logger.info("cookies:%s",cookies)
    return cookies

def process(content, wechatcrawler, wechatprocess):
    # j = json.loads(content)
    # infos = j["value"]
    # logger.info("Got %s news", len(infos))
    cnt = 0
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    logger.info("title: %s", title)

    download_crawler = download.DownloadCrawler(use_proxy=False)

    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    for li in d('div.news-box> ul.news-list>li'):
        try:

            title = d(li)('h3> a').text()
            title = "".join(title.split(" "))
            wexinlink =  d(li)('h3> a').attr("href").strip()
            post_time = d('div.s-p').attr("t")
            logger.info(post_time)
            try:

                post_time = time.localtime(int(post_time))
                news_time = datetime.datetime(post_time.tm_year, post_time.tm_mon, post_time.tm_mday, post_time.tm_hour,
                                         post_time.tm_min, post_time.tm_sec)
                if news_time is None:
                    news_time = datetime.datetime.now()
            except:
                news_time = datetime.datetime.now()
            logger.info("link: %s", wexinlink)
            logger.info("article : %s,%s", title, news_time)

            item = collection_news.find_one({"link": wexinlink})
            item2 = collection_news.find_one({"title": title})
            # # item2 = collection_news.find_one({"title": title})
            # logger.info(item)
            # logger.info(item2)
            if item is None and item2 is None:
                logger.info("here crawler")
                dnews = wechatprocess.crawler_news(wechatcrawler, wexinlink, download_crawler, wechatId="微信公众号")

                # dnews["wechatId"] = wechatId
                # dnews["wechatName"] = wechatName
                dnews["title"] = title
                dnews["date"] = news_time - datetime.timedelta(hours=8)
                dnews["processStatus"] = 0
                dnews["imgChecked"] = True
                dnews["category"] = None

                if dnews["result"] == 'SUCCESS' and len(dnews["contents"])>=1:
                    dnews.pop('result')
                    try:
                        id = collection_news.insert(dnews)
                        logger.info("**************: %s", id)
                        cnt += 1
                    except Exception, e:
                        logger.info(e)
                        pass
        except:
            pass

    mongo.close()
    return cnt


if __name__ == "__main__":
    # display = Display(visible=0, size=(1280, 800))
    # display.start()
    # time.sleep(5)
    while True:
        get()
        # time.sleep(60*60)
        # gen_cookie()
        break
    # display.stop()
