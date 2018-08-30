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
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import util, name_helper, url_helper, download, db,oss2_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../crawler'))
import BaseCrawler

#logger
loghelper.init_logger("yitai_pdf", stream=True)
logger = loghelper.get_logger("yitai_pdf")

download_crawler = download.DownloadCrawler(use_proxy=False)

#parse data from qimingpian directly, bamy called it step 1 to checkout company


crawler = BaseCrawler.BaseCrawler(use_proxy=False)


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
    return None, None


@set_timeout(20, after_timeout)
def getPage(file_path):
    fp = open(file_path, "rb")
    try:
    # fp = open(file_path, "rb")
        pdfReader = PdfFileReader(fp)
        logger.info("read done")
        if pdfReader.isEncrypted:
            fp.close()
            logger.info("File encrypted! filename: %s", file_path)
            decrypt_pdf(file_path)
            fp = file(file_path, "rb")
            pdfReader = PdfFileReader(fp)
            page = pdfReader.getNumPages()
        else:
            page = pdfReader.getNumPages()

        creationDater = pdfReader.documentInfo.get("/CreationDate")
        if not isinstance(creationDater, str):

            creationDater = creationDater.getObject()

        logger.info("here dta: %s", creationDater)
        if creationDater.find("+") >= 0:

            datestring = creationDater[2:-7]
        else:
            datestring = creationDater[2:15]
        creationDate = datetime.datetime.strptime(datestring, "%Y%m%d%H%M%S")

    except Exception, e:
        logger.info("here worn   %s",e)
        time.sleep(4)
        page = None
        creationDate = None

    fp.close()
    return page, creationDate

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
        pages, pdfcreationDate = getPage(file_path)
        if pdfcreationDate is None:
            return False
        # fp.close()
        size = os.path.getsize(file_path)


        md5 = util.get_file_md5(file_path)

        if check_file_exists(md5,rep["title"]):
            return False

        fileid = util.get_uuid()
        logger.info("%s, %s, %s, %s, %s, %s", rep["title"], size, pdfcreationDate, pages, md5, fileid)


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
                "pdfCreationDate": pdfcreationDate,
                "pages": pages,
                "md5": md5,
                "fileid": fileid,
                "createTime": datetime.datetime.now() - datetime.timedelta(hours=8),
                "modifyTime": datetime.datetime.now() - datetime.timedelta(hours=8),
                "type": 78001
            }
        )
        mongo.close()
        return True



def parse_company(item):


    rpnew = {
        # "source": None,

        "title": item["title"],
        "filename": item["title"] + ".pdf",
        "source": None,
        "durl": item["link"]

    }
    return rpnew



if __name__ == '__main__':
    logger.info("card pdf Begin...")
    # i = {"title":"40页PPT全景展示雄安主题：笑看风云平地起-20170809-华创证券-40页",
    #      "link":"https://file.ethercap.com/ether-public/up/report/27971e68d38b1ef816151188d8211e7dfa381"}
    # report = parse_company(i)
    # process(report)
    tot = 0
    tot1 = 0
    tot2 = 0
    fp = open("yitai_rp.txt")
    lines = fp.readlines()
    for line in lines:
        logger.info("%s/%s/%s", tot, tot1, tot2)
        names = [name.strip() for name in line.strip().split("+++")]
        if len(names) != 3:
            logger.info(line)
            exit()
        tot += 1
        t = names[1]
        link = names[2]
        if link.find("http") == -1 or t.strip() == "":
            continue
        i = {
            "title": t.replace(".pdf",""),
            "link": link
        }
        report = parse_company(i)
        logger.info(json.dumps(report, ensure_ascii=False, cls=util.CJsonEncoder))
        if report.has_key("title") is True and check(report["title"]):
            tot1 += 1
            f = process(report)

            if f is True:
                tot2 += 1

        logger.info("%s/%s/%s", tot, tot1, tot2)
    # noo = 0
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
        # break
