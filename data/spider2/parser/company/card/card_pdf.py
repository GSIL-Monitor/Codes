# -*- coding: utf-8 -*-
import os, sys, re
import signal
import time
import datetime
from bson.objectid import ObjectId
import json


from PyPDF2 import PdfFileReader
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, name_helper, url_helper, download, db,oss2_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler'))
import BaseCrawler

#logger
loghelper.init_logger("card_pdf", stream=True)
logger = loghelper.get_logger("card_pdf")

download_crawler = download.DownloadCrawler(use_proxy=True)
SOURCE = 13121
#parse data from qimingpian directly, bamy called it step 1 to checkout company


crawler = BaseCrawler.BaseCrawler()


def decrypt_pdf(file_path):
    command = (""
               "cp '" + file_path + "' /data/ftp/temp.pdf; "
               "qpdf --password='' --decrypt /data/ftp/temp.pdf '" + file_path + "'; "
               "rm /data/ftp/temp.pdf; ")
    os.system(command)

def delete():
    file_path = "download.pdf"
    if os.path.isfile(file_path):
        command = ("rm download.pdf; ")
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
    fileName = 'download.pdf'
    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], fileName)

    logger.info('saving file:%s', path)
    with open(path, "wb") as file:
        file.write(content)

    return fileName


def run(link):
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

def process(rep):
    res = 0
    while True:
        delete()
        res += 1
        if res > 20:
            return False
        run(rep["durl"])
        logger.info("saving done")
        file_path = "download.pdf"
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



def parse_company(item):
    rps = []
    if item.has_key("data") is False:
        return []
    if item["data"].has_key("items") is False:
        return []
    for rp in item["data"]["items"]:
        if rp.has_key("name") is False or rp["name"] is None or rp["name"].find("pdf") == -1:
            continue
        title = rp["name"].split("-")[0].strip()
        if title.find("速途") >= 0:
            continue
        source = rp["report_source"]
        if source.find("速途") >= 0:
            continue
        try:
            cdate = datetime.datetime.strptime(rp["update_time"], "%Y-%m-%d %H:%M:%S")
        except:
            continue
        filename = title + ".pdf"

        rpnew = {
            # "source": None,
            "description": None,
            "title": title,
            "filename": filename,
            "pdfCreationDate": cdate,
            "source": source if source is not None and source.find("企名片") == -1 else None,
            "durl": rp["url"]
        }
        rps.append(rpnew)

    return rps


if __name__ == '__main__':
    logger.info("card pdf Begin...")
    # noo = 0
    while True:
        (num0, num1, num2, num3, num4, num5, num6, num7) = (0, 0, 0, 0, 0, 0, 0, 0)
        conn = db.connect_torndb()
        mongo = db.connect_mongo()
        collection = mongo.raw.qmp

        while True:
            # items = list(collection.find({"_id" : ObjectId("5ad7ef121045403178ed4135")}).limit(100))
            items = list(collection.find({"url":"http://pdf.api.qimingpian.com/t/getFileByPage1","processed":None},
                                         {"data":1,"postdata":1,"url":1}))
            logger.info("items : %s", len(items))
            for item in items:
                logger.info(item)
                reports = parse_company(item)
                for report in reports:

                    logger.info(json.dumps(report, ensure_ascii=False, cls=util.CJsonEncoder))
                    # if check(report["title"]) and report["title"].find("空巢青年租房数据报告") == -1:
                    if check(report["title"]):
                        process(report)
                        # break
                    else:
                        logger.info("already existed")

                logger.info("processed %s", item["url"])
                collection.update_one({"_id":item["_id"]},{'$set':{"processed":True}})
                # break

            break
        # logger.info("%s - %s - %s - %s - %s - %s - %s - %s", num0, num1, num2, num3, num4, num5, num6, num7)
        mongo.close()
        conn.close()
        time.sleep(10*60)
        # break
