# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, urllib,time
from lxml import html
from pyquery import PyQuery as pq
import signal
from PyPDF2 import PdfFileReader

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download, extractArticlePublishedDate, oss2_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_irui_report", stream=True)
logger = loghelper.get_logger("crawler_irui_report")

NEWSSOURCE = "irui"
RETRY = 3
FILE = "irui_download.pdf"
SOURCE = "艾瑞"
URLS = []
CURRENT_PAGE = 1
Nocontents = [
]
columns = [
    {"column": "business", "max": 1},
    # {"column": "company", "max": 1},
    # {"column": "article", "max": 1},
]

crawler = BaseCrawler.BaseCrawler()


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
    fileName = 'irui_download.pdf'
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
        file_path = "irui_download.pdf"
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
                "type": 78001,
            }
        )
        mongo.close()
        return True



class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("gbk")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " " + url)

        if title.find("艾瑞网") >= 0:
            return True
        # logger.info(content)
        return False


def process_list(content):
    d = pq(html.fromstring(content.decode("gbk")))
    lis = d("ul#ulroot3> li")
    # logger.info(lis)
    for li in lis:
        l = pq(li)
        id = l('li').attr("id").strip()
        title = l("div.txt> h3").text().strip()
        href = l("div.txt> h3> a").attr("href").strip()
        news_key = href.split("/")[-1].replace(".shtml", "")
        news_url = href
        news_time = l('div.txt> div> div.time').text().strip()


        logger.info("%s, %s, %s, %s, %s", id, title, news_key, news_url, news_time)

        if check(title) is True:

            item = {
                "key": news_key,
                "link": news_url,
                "description": None,
                "title": title,
                "filename": title + '.pdf',
                "pdfCreationDate": datetime.datetime.strptime(news_time,"%Y/%m/%d %H:%M:%S"),
                "source": SOURCE,
                "durl": 'http://report.iresearch.cn/include/ajax/user_ajax.ashx?reportid=%s&work=rdown&url=%s' % (news_key, news_url)
            }
            URLS.append(item)
    return len(URLS)


def run_list(listcrawler):
    global CURRENT_PAGE

    url = "http://report.iresearch.cn/"

    while True:
        result = listcrawler.crawl(url,agent=True)

        if result['get'] == 'success':
            try:
                cnt = process_list(result['content'])
                if cnt > 0:
                    logger.info("%s has %s fresh news", url, cnt)
                    logger.info(URLS)
                    run_news()

                    # exit()
            except Exception,ex:
                logger.exception(ex)
                cnt = 0
            break



def start_run():
    global CURRENT_PAGE
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