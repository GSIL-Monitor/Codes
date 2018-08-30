# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, urllib, time
from lxml import html
from pyquery import PyQuery as pq
import signal
from PyPDF2 import PdfFileReader

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, extract, db, util, url_helper, download, extractArticlePublishedDate, oss2_helper,traceback_decorator

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

# logger
loghelper.init_logger("crawler_iyiou_report", stream=True)
logger = loghelper.get_logger("crawler_iyiou_report")

NEWSSOURCE = "yiou"
RETRY = 3
SOURCE = "亿欧"
URLS = []
CURRENT_PAGE = 1
linkPattern = "https://www.iyiou.com/intelligence/report\d+"


crawler = BaseCrawler.BaseCrawler()

def decrypt_pdf(file_path):
    command = (""
               "cp '" + file_path + "' /data/ftp/temp.pdf; "
               "qpdf --password='' --decrypt /data/ftp/temp.pdf '" + file_path + "'; "
               "rm /data/ftp/temp.pdf; ")
    os.system(command)

def delete():
    file_path = "yiou_download.pdf"
    if os.path.isfile(file_path):
        command = ("rm yiou_download.pdf; ")
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
    fileName = 'yiou_download.pdf'
    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], fileName)
    logger.info('saving file:%s', path)
    with open(path, "wb") as file:
        file.write(content)

    return fileName


def to_run(link):
    url = link
    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            save_marketdata(result['content'])
            break


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

def process_pdf(rep):
    res = 0
    while True:
        delete()
        res += 1
        if res > 20:
            return False
        to_run(rep["durl"])
        logger.info("saving done")
        file_path = "yiou_download.pdf"
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
                "createTime": rep["pdfCreationDate"]- datetime.timedelta(hours=8),
                "modifyTime": rep["pdfCreationDate"]- datetime.timedelta(hours=8),
                "type": 78001,
            }
        )
        mongo.close()
        return True

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("亿欧智库") >= 0:
            return True
        return False

def run_news():
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)
        logger.info(json.dumps(URL, ensure_ascii=False, indent=2, cls=util.CJsonEncoder))
        process_pdf(URL)


def process_list(content):
    logger.info('start to process list  page')
    if content.find('iyiou') >= 0:
        d = pq(html.fromstring(content.decode("utf-8")))
        lis = d('li.liLists')
        for li in lis:
            try:
                link = 'https://www.iyiou.com' + d(li)('div.business> a').attr('href')
                title = d(li)('div.desc> span').text().strip()
                if re.search(linkPattern, link) and title is not None and title.strip() != "":
                    key = link.split('report')[-1]
                    description = None
                    filename = title + '.pdf'
                    date = d(li)('div.bottom> span> i').text().strip()
                    dates = map(int, date.strip().split('-'))
                    pdfCreationDate = datetime.datetime(dates[0], dates[1], dates[2])
                    durl = 'https://www.iyiou.com/intelligence/download?id=%s'%key
                    logger.info("Link: %s is right news link ---> %s|%s", link, title, date)

                    if check(title):
                        linkmap = {
                            'key': key,
                            "link": link,
                            'title': title,
                            'filename': filename,
                            'source': SOURCE,
                            'pdfCreationDate':pdfCreationDate,
                            'description':description,
                            'durl':durl
                        }
                        URLS.append(linkmap)

            except Exception, e:
                logger.info(e)
                logger.info("cannot get link")
    return len(URLS)


def run(listcrawler):
    cnt = 1
    if cnt == 0 :
        return
    for i in range(1,5):
        url = "https://www.iyiou.com/intelligence/report?page=%d" % i
        while True:
            result = listcrawler.crawl(url, agent=True)

            if result['get'] == 'success':
                try:
                    cnt = process_list(result['content'])
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        run_news()

                except Exception, ex:
                    logger.exception(ex)
                    cnt = 0
                break

@traceback_decorator.try_except
def start_run():
    logger.info('the date:%s'%datetime.datetime.now())
    while True:
        logger.info("%s report  start...", NEWSSOURCE)
        listcrawler = ListCrawler()
        run(listcrawler)

        logger.info("%s report end.", NEWSSOURCE)
        time.sleep(60 * 60 * 6)  # 6 hours


if __name__ == "__main__":
        start_run()
