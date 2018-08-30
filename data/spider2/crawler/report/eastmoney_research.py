# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, urllib,time
from lxml import html
from pyquery import PyQuery as pq
import signal
from PyPDF2 import PdfFileReader

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler2

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download, extractArticlePublishedDate, oss2_helper,traceback_decorator

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_eastm_report", stream=True)
logger = loghelper.get_logger("crawler_eastm_report")

NEWSSOURCE = "eastm"
RETRY = 3
FILE = "eastm_download.pdf"
SOURCE = None
URLS = []
CURRENT_PAGE = 1
Nocontents = [
]
columns = [
    {"column": "business", "max": 1},
    # {"column": "company", "max": 1},
    # {"column": "article", "max": 1},
]

crawler = BaseCrawler2.BaseCrawler()


def decrypt_pdf(file_path):
    command = (""
               "cp '" + file_path + "' /data/ftp/temp.pdf; "
               "qpdf --password='' --decrypt /data/ftp/temp.pdf '" + file_path + "'; "
               "rm /data/ftp/temp.pdf; ")
    os.system(command)

def delete():
    file_path = "irui_download.pdf"
    if os.path.isfile(file_path):
        command = ("rm irui_download.pdf; ")
        os.system(command)

def check_file_exists(md5,title):
    mongo = db.connect_mongo()
    r = mongo.article.report.find_one({"md5": md5})
    r1 = mongo.article.report.find_one({"title": title})
    mongo.close()
    if r is not None and r1 is not None:
        return True
    return False

def check(title):
    mongo = db.connect_mongo()
    r1 = mongo.article.report.find_one({"title": title})
    mongo.close()
    if r1 is None:
        return True
    return False

def save_marketdata(content):
    fileName = 'eastm_download.pdf'
    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], fileName)

    logger.info('saving file:%s', path)
    with open(path, "wb") as file:
        file.write(content)

    return fileName


def run(link):
    url = link
    nheaders = {
        "Cookie": " iRsCookieId=52a55a51a52a54a52a48a50a49a48a48a50a54a48a56a49;iRsUserId=55a48a51a55a53a48a49;iRsUserAccount=109a111a99a46a97a110a105a115a64a117a120a105a101a108a110a117a106; iRsUserPassword=117a120a121a109a97a98a48a52a53;",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    }
    retry = 0
    while True:
        result = crawler.crawl(url, agent=True, headers=nheaders)
        if result['get'] == 'success':
            save_marketdata(result['content'])
            break
        retry += 1
        if retry > 8:
            break

def run_news():
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        process(URL)
        time.sleep(10)

def set_timeout(num, callback):
    def wrap(func):
        def handle(signum, frame):  # 收到信号 SIGALRM 后的回调函数，第一个参数是信号的数字，第二个参数是the interrupted stack frame.
            raise RuntimeError

        def to_do(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handle)  # 设置信号和回调函数
                signal.alarm(num)  # 设置 num 秒的闹钟
                logger.info('start alarm signal.')
                r = func(*args, **kwargs)
                logger.info('close alarm signal.')
                signal.alarm(0)  # 关闭闹钟
                return r
            except RuntimeError as e:
                callback()

        return to_do

    return wrap

def after_timeout():
    logger.info("long time")
    return None


@set_timeout(20, after_timeout)
def getPage(file_path):
    fp = open(file_path, "rb")
    try:
    # fp = open(file_path, "rb")
        pdfReader = PdfFileReader(fp)
        logger.info("read done")
        if pdfReader.isEncrypted:
            page = None
        else:
            page = pdfReader.getNumPages()

    except Exception, e:
        logger.info("here worn   %s",e)
        time.sleep(4)
        page = None

    fp.close()
    return page

def process(rep):
    res = 0
    while True:
        delete()
        res += 1
        if res > 20:
            return False
        run(rep["durl"])
        logger.info("saving done")
        file_path = "eastm_download.pdf"
        if not os.path.isfile(file_path):
            return False

        # logger.info(file_path)
        # try:
        #     fp = open(file_path, "rb")
        #     pdfReader = PdfFileReader(fp)
        #     logger.info("read done")
        #     if pdfReader.isEncrypted:
        #         return False
        #
        # except:
        #     continue
        # pages = pdfReader.getNumPages()
        pages = getPage(file_path)
        # fp.close()
        size = os.path.getsize(file_path)


        md5 = util.get_file_md5(file_path)

        if check_file_exists(md5,rep["title"]):
            return True

        fileid = util.get_uuid()
        logger.info("%s, %s, %s, %s, %s, %s", rep["title"], size, rep["pdfCreationDate"], pages, md5, fileid)

        oss = oss2_helper.Oss2Helper("xiniudata-report")
        fp = file(file_path, "rb")
        oss.put(fileid, fp, headers={"Content-Type": "application/pdf", "x-oss-meta-filename": rep["filename"]})
        fp.close()

        mongo = db.connect_mongo()
        mongo.article.report.insert_one(
            {
                "source": rep["source"],
                "description": None,
                "title": rep["title"],
                "filename": rep["filename"],
                "size": size,
                "pdfCreationDate": rep["pdfCreationDate"]-datetime.timedelta(hours=8),
                "pages": pages,
                "md5": md5,
                "fileid": fileid,
                "createTime": datetime.datetime.now() - datetime.timedelta(hours=8),
                "modifyTime": datetime.datetime.now() - datetime.timedelta(hours=8),
                "type": 78004,
            }
        )
        mongo.close()
        return True



class ListCrawler(BaseCrawler2.BaseCrawler):
    def __init__(self):
        BaseCrawler2.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content,redirect_url):
        if content.find("([") >= 0:
            try:
                c = content.decode("gbk", "ignore")
                j = eval(c.replace("null", "\"abcnull\""))
                if len(j) > 0:
                    return True
                else:
                    return False
            except Exception,E:
                logger.info("here")
                logger.info(E)
                return False

class espCrawler(BaseCrawler2.BaseCrawler):
    def __init__(self):
        BaseCrawler2.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content,redirect_url):
        if redirect_url.find("pdf") >= 0:
            logger.info("get: %s", redirect_url)
            return True
        else:

            if content.find("</html>") == -1:
                return False
            # logger.info(content)
            d = pq(html.fromstring(content.decode("gbk","ignore")))
            title = d('head> title').text().strip()
            # logger.info("title: " + title + " " + url)

            if title.find("东方财富") >= 0:
                return True
        # logger.info(content)
        return False

espcralwer = espCrawler()
def crawler_rp(nurl, nctitle, ndate):
    retry = 0
    pdflink = None
    while True:
        result = espcralwer.crawl(nurl, agent=True)
        if result['get'] == 'success':
            if result["redirect_url"].find("pdf") >= 0:
                logger.info("we got pdf : %s ",result["redirect_url"])
                pdflink = result["redirect_url"],
            else:
                try:
                    d = pq(html.fromstring(result["content"].decode('gbk', 'ignore')))
                    filelink = d('div.report-content> span> a').attr("href")
                    if filelink is not None and filelink.find("pdf") >= 0:
                        pdflink = filelink
                except Exception, ex:
                    logger.exception(ex)
            break

        retry += 1
        if retry > 18: break
    return pdflink

def process_list(content):
    # c = content.decode("gbk", "ignore")
    c = content
    infos = eval(c.replace("null", "\"abcnull\""))
    mongo = db.connect_mongo()

    collection = mongo.article.report
    for info in infos:
        infons = info.split(",")
        # for inf in infons:
        #     logger.info(inf)
        ntitle = infons[9].replace("&sbquo;","，").replace("&quot;","\"")
        ndate = infons[1]
        nurl = infons[2]
        cleantitle = ntitle.split("：")[1].replace("&sbquo;","，").replace("&quot;","\"")
        logger.info("%s-%s-%s-%s", ntitle, cleantitle, ndate,nurl)

        item = collection.find_one({"title": cleantitle})
        item1 = collection.find_one({"title": ntitle})
        if item is not None or item1 is not None:
            logger.info("******already exists")
        else:
            logger.info("******missing, get it")
            rpdate = datetime.datetime.strptime(ndate, '%Y/%m/%d %H:%M:%S')
            rpdate_str = rpdate.strftime('%Y%m%d')
            link ='http://data.eastmoney.com/report/%s/hy,%s.html' % (rpdate_str, nurl)
            logger.info("need to crawler: %s", link)
            plink = crawler_rp(link, ntitle, rpdate)
            if plink is not None:
                logger.info("*******\nhere is pdf link: %s\n", plink)
            # crawler_rp(nurl, cleantitle, ndate, sourceId, source)
                item = {
                    "key": nurl,
                    "link": link,
                    "description": None,
                    "title": ntitle,
                    "filename": ntitle + '.pdf',
                    "pdfCreationDate": rpdate,
                    "source": SOURCE,
                    "durl": plink
                }
                URLS.append(item)
                if len(URLS) > 5:
                    break


    mongo.close()

    return len(URLS)


def run_list(listcrawler):
    key = 1
    while True:

        url = 'http://datainterface.eastmoney.com//EM_DataCenter/js.aspx?type=SR&sty=HYSR&mkt=0&stat=0&cmd=4&code=&sc=&ps=50&p=%s' % (key)
        # data = '{"code":"%s","part":{"brief":"{brief}"}}' % sourceId
        # headers = {"Content-Type": "application/json"}

        cnt1 = 0
        while True:
            result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    # logger.info(result['content'], sourceId, source)
                    cnt1 = process_list(result['content'])
                    if cnt1 > 0:
                        logger.info("%s has %s fresh news", url, cnt1)
                        logger.info(URLS)
                        run_news()

                except Exception, ex:
                    logger.exception(ex)

                break
        if cnt1 > 0:
            key += 1
        else:
            break


# @traceback_decorator.try_except
def start_run():
    while True:
        logger.info("%s report start...", NEWSSOURCE)
        listcrawler = ListCrawler()

        CURRENT_PAGE = 1
        run_list(listcrawler)

        logger.info("%s report end.", NEWSSOURCE)

        time.sleep(10*300)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pass
    else:
        start_run()