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
import util, name_helper, url_helper, download, db,oss2_helper,traceback_decorator

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler'))
import BaseCrawler

#logger
loghelper.init_logger("card_pdf", stream=True)
logger = loghelper.get_logger("card_pdf")

download_crawler = download.DownloadCrawler(use_proxy=False)

#parse data from qimingpian directly, bamy called it step 1 to checkout company


crawler = BaseCrawler.BaseCrawler(use_proxy=False)
source_map = {
    13400: "新三板",
    13401: "上证",
    13402: "深证"
}

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
    retry = 0
    while True:
        retry += 1
        if retry > 20:
            break
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
                "pdfCreationDate": rep["pdfCreationDate"],
                "pages": pages,
                "md5": md5,
                "fileid": fileid,
                "createTime": rep["createTime"]- datetime.timedelta(hours=8),
                "modifyTime": rep["createTime"]- datetime.timedelta(hours=8),
                "type": 78003 if rep["marketSource"] is not None and  rep["marketSource"] == "新三板" else 78002,
                "marketSource": rep["marketSource"],
                "marketSymbol": rep["marketSymbol"],
            }
        )
        mongo.close()
        return True



def parse_company(item):

    if item.has_key("title") is False:
        return {}
    if item.has_key("link") is False:
        return {}
    if item["link"].find("pdf") == -1 and item["link"].find("PDF") == -1:
        return {}

    rflag = False
    if item["source"] in [13401,13402] and item["title"].find("首次公开发行股票") >= 0 and \
            item["title"].find("招股说明书") >= 0 and item["title"].find("附录") == -1:
        rflag = True

    # if item["source"] in [13401,13402] and item["title"].find("首次公开发行股票") >= 0 and \
    #         item["title"].find("招股意向书") >= 0 and  item["title"].find("附录") == -1:
    #     rflag = True
    if item["source"] in [13400] and item["title"].find("公开转让说明书") >= 0:
        rflag = True

    if rflag is True:
        rpnew = {
            # "source": None,
            "description": None,
            "title": item["title"],
            "filename": item["title"] + ".pdf",
            "pdfCreationDate": item["date"],
            "source": None,
            "durl": item["link"],
            "marketSource": source_map.get(item["source"],None),
            "marketSymbol": item["stockSymbol"],
            "createTime": item["createTime"]

        }
        return rpnew
    else:
        return {}


@traceback_decorator.try_except
def run_b():
    logger.info("card pdf Begin...")
    # noo = 0
    while True:
        (num0, num1, num2, num3, num4, num5, num6, num7) = (0, 0, 0, 0, 0, 0, 0, 0)
        conn = db.connect_torndb()
        mongo = db.connect_mongo()
        collection = mongo.stock.announcement

        while True:
            items = list(collection.find({"rpchecked": None}).limit(2000))
            # items = list(collection.find({}))
            logger.info("items : %s", len(items))
            for item in items:
                # logger.info(item)
                report = parse_company(item)

                # logger.info(json.dumps(report, ensure_ascii=False, cls=util.CJsonEncoder))

                if report.has_key("title") is True and check(report["title"]):
                    logger.info("%s \t%s", report["marketSource"], report["title"])
                    # num0 += 1
                    process(report)
                    # break
                else:
                    pass
                    # logger.info("already existed")
                collection.update_one({"_id": item["_id"]}, {"$set": {"rpchecked": True}})
                # break
            if len(items) == 0:
                break
        # logger.info("%s - %s - %s - %s - %s - %s - %s - %s", num0, num1, num2, num3, num4, num5, num6, num7)
        mongo.close()
        conn.close()
        time.sleep(10 * 60)

if __name__ == '__main__':
    # logger.info("card pdf Begin...")
    # # noo = 0
    # while True:
    #     (num0, num1, num2, num3, num4, num5, num6, num7) = (0, 0, 0, 0, 0, 0, 0, 0)
    #     conn = db.connect_torndb()
    #     mongo = db.connect_mongo()
    #     collection = mongo.stock.announcement
    #
    #     while True:
    #         items = list(collection.find({"rpchecked":None}).limit(2000))
    #         # items = list(collection.find({}))
    #         logger.info("items : %s", len(items))
    #         for item in items:
    #             # logger.info(item)
    #             report = parse_company(item)
    #
    #             # logger.info(json.dumps(report, ensure_ascii=False, cls=util.CJsonEncoder))
    #
    #             if report.has_key("title") is True and check(report["title"]):
    #                 logger.info("%s \t%s",report["marketSource"],report["title"])
    #                 # num0 += 1
    #                 process(report)
    #                 # break
    #             else:
    #                 pass
    #                 # logger.info("already existed")
    #             collection.update_one({"_id":item["_id"]},{"$set":{"rpchecked":True}})
    #             # break
    #         if len(items) == 0:
    #
    #             break
    #     # logger.info("%s - %s - %s - %s - %s - %s - %s - %s", num0, num1, num2, num3, num4, num5, num6, num7)
    #     mongo.close()
    #     conn.close()
    #     time.sleep(10*60)
    #     # break
    run_b()
