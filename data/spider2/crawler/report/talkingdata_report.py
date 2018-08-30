# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, urllib, time
from lxml import html
from pyquery import PyQuery as pq
import signal
from PyPDF2 import PdfFileReader
from urllib import quote

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
loghelper.init_logger("crawler_talkingdata_report", stream=True)
logger = loghelper.get_logger("crawler_talkingdata_report")

NEWSSOURCE = "talkingdata"
RETRY = 3
TYPE = 60005
SOURCE = "移动观象台"
URLS = []
CURRENT_PAGE = 1
linkPattern = "http://mi.talkingdata.com/report-detail.html\?id=\d+"
crawler = BaseCrawler.BaseCrawler()

def decrypt_pdf(file_path):
    command = (""
               "cp '" + file_path + "' /data/ftp/temp.pdf; "
               "qpdf --password='' --decrypt /data/ftp/temp.pdf '" + file_path + "'; "
               "rm /data/ftp/temp.pdf; ")
    os.system(command)

def delete():
    file_path = "talkingdata_download.pdf"
    if os.path.isfile(file_path):
        command = ("rm talkingdata_download.pdf; ")
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
    fileName = 'talkingdata_download.pdf'
    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], fileName)
    logger.info('saving file:%s', path)
    with open(path, "wb") as file:
        file.write(content)
    return fileName


def to_run(link):
    link = link.encode('utf-8')
    url = 'http://doc.talkingdata.com/reports/archives/pdf/' + quote(link.split('pdf/')[-1])
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
        file_path = "talkingdata_download.pdf"
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
        if size == 0:
            return False


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
        if title.find("TalkingData") >= 0 or content.find('talkingdata') >= 0:
            return True
        return False

def process_news(rep,content,):
    url = rep['link']
    logger.info('start to process detail page:%s'%url)
    if content.find('TalkingData') >= 0:
        d = pq(html.fromstring(content.decode("utf-8")))
        title = rep['title']
        durl = d('div.operate-verify> button').attr('data-url')
        if durl == 'http://doc.talkingdata.com/reports':
            return
        if durl is not None and title is not None and title.strip() != '':
            date = rep['ddate']
            dates = map(int,date.strip().split('-'))
            pdfCreationDate = datetime.datetime(dates[0],dates[1],dates[2])
            rep['pdfCreationDate'] = pdfCreationDate
            rep['durl'] = durl
            rep['description'] = None
            del rep['ddate']
            logger.info(json.dumps(rep,ensure_ascii=False,indent=2,cls=util.CJsonEncoder))
            process_pdf(rep)

def crawler_news(crawler, URL):
    retry = 0
    while True:
        url = URL['link']
        result = crawler.crawl(url, agent=True)

        if result['get'] == 'success':
            try:
                process_news(URL, result['content'],)
            except Exception, ex:
                logger.exception(ex)
            break
        retry += 1
        if retry > 20: break

def run_news(crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)
        crawler_news( crawler,URL)

def process_list(content):
    logger.info('start to process list page')
    if content.find('TalkingData') >= 0:
        d = pq(html.fromstring(content.decode("utf-8")))
        divs = d('div.results-list> div.results')
        logger.info('pdf counts:%d'%len(divs))
        for a in divs:
            try:
                link = d(a)('a.clearfix').attr('href')
                title = d(a)('a.clearfix> dl> dt').text()
                if re.search(linkPattern, link) and title is not None and title.strip() != "":
                    ddate = d(a)('a.clearfix> dl> dd').text()
                    key = link.split('=')[-1]
                    # logger.info("Link: %s is right news link ---> %s|%s", link, title, ddate)

                    if check(title):
                        linkmap = {
                            'key':key,
                            "link": link,
                            'title':title,
                            "ddate": ddate,
                            'filename':title + '.pdf',
                            'source':SOURCE,
                        }
                        URLS.append(linkmap)
                    # else:
                    #     pass # 此source 有300多条 但存进这个source的只有200多条 说明其他源已经存过其他的100多条相同title的pdf
            except Exception,e:
                logger.info(e)
                logger.info("cannot get link")
    return len(URLS)

def run(listcrawler):
    cnt = 1
    if cnt == 0 :
        return

    url = "http://mi.talkingdata.com/allReports.html"

    while True:
        result = listcrawler.crawl(url, agent=True)

        if result['get'] == 'success':
            try:
                cnt = process_list(result['content'])
                if cnt > 0:
                    logger.info("%s has %s fresh news", url, cnt)
                    # logger.info(URLS)
                    run_news(listcrawler)

            except Exception, ex:
                logger.exception(ex)
                cnt = 0
            break

@traceback_decorator.try_except
def start_run():
    logger.info('the date:%s'%datetime.datetime.now())
    while True:
        logger.info("%s report start...", NEWSSOURCE)
        listcrawler = ListCrawler()
        run(listcrawler)

        logger.info("%s report end.", NEWSSOURCE)
        time.sleep(60 * 60 * 6)  # 6 hours


if __name__ == "__main__":
    start_run()
