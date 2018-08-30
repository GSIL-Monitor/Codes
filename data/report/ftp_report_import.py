# -*- coding: utf-8 -*-
import os, sys
import time
from datetime import datetime, timedelta
import traceback
from PyPDF2 import PdfFileReader

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util, oss2_helper

#logger
loghelper.init_logger("ftp_report_import", stream=True)
logger = loghelper.get_logger("ftp_report_import")


def decrypt_pdf(file_path):
    command = ("export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH; "
               "cp '" + file_path + "' /data/ftp/temp.pdf; "
               "qpdf --password='' --decrypt /data/ftp/temp.pdf '" + file_path + "'; "
               "rm /data/ftp/temp.pdf; ")
    os.system(command)


def process(dir_path, filename):
    # logger.info(filename)
    file_path = os.path.join(dir_path, filename)
    if not os.path.isfile(file_path):
        return False
    if not filename.lower().endswith(".pdf"):
        return False
    # logger.info(file_path)

    fp = file(file_path, "rb")
    pdfReader = PdfFileReader(fp)
    if pdfReader.isEncrypted:
        fp.close()
        logger.info("File encrypted! filename: %s", filename)
        decrypt_pdf(file_path)
        fp = file(file_path, "rb")
        pdfReader = PdfFileReader(fp)

    # creationDate = pdfReader.documentInfo.get("/CreationDate")
    # if not isinstance(creationDate, str):
    #     try:
    #         creationDate = creationDate.getObject()
    #     except:
    #         traceback.print_exc()
    #         return False

    pages = pdfReader.getNumPages()
    fp.close()

    # try:
    #     datestring = creationDate[2:-7]
    #     ts = strptime(datestring, "%Y%m%d%H%M%S")
    # except:
    #     traceback.print_exc()
    #     return False
    # dt = datetime.fromtimestamp(mktime(ts)) - timedelta(hours=8)
    ts = os.path.getctime(file_path)
    dt = datetime.fromtimestamp(ts) - timedelta(hours=8)

    size = os.path.getsize(file_path)
    title = filename[0:-4].strip()
    source = None
    if u"：" in title:
        strs = title.split(u"：", 1)
        source = strs[0]
        title = strs[1]

    md5 = util.get_file_md5(file_path)

    if check_file_exists(md5, title):
        return True

    fileid = util.get_uuid()
    logger.info("%s, %s, %s, %s, %s, %s", title, size, dt, pages, md5, fileid)

    oss = oss2_helper.Oss2Helper("xiniudata-report")
    fp = file(file_path, "rb")
    oss.put(fileid, fp, headers={"Content-Type": "application/pdf", "x-oss-meta-filename": filename.strip()})
    fp.close()

    save(source, filename, title, size, dt, pages, md5, fileid)
    return True


def save(source, filename, title, size, dt, pages, md5, fileid):
    mongo = db.connect_mongo()
    mongo.article.report.insert_one(
        {
            "source": source,
            "description": None,
            "title": title,
            "filename": filename,
            "size": size,
            "pdfCreationDate": dt,
            "pages": pages,
            "md5": md5,
            "fileid": fileid,
            "createTime": dt,
            "modifyTime": dt,
            "type": 78001
        }
    )
    mongo.close()


def check_file_exists(md5, title):
    mongo = db.connect_mongo()
    r = mongo.article.report.find_one({"md5": md5})
    if r is not None:
        mongo.close()
        return True

    r = mongo.article.report.find_one({"title": title})
    if r is not None:
        mongo.close()
        return True

    mongo.close()
    return False


def main():
    dir_path = "/data/ftp/"
    files = os.listdir(dir_path)
    for filename in files:
        try:
            flag = process(dir_path, filename)
            if flag:
                os.chdir(dir_path)
                os.remove(filename)
            # exit()
        except:
            traceback.print_exc()


if __name__ == '__main__':
    while True:
        main()
        time.sleep(60)