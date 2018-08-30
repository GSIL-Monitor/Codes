# -*- coding: utf-8 -*-
import os, sys,datetime
import subprocess
import threading
import gridfs
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db
import loghelper


#logger
loghelper.init_logger("crawler_screenshot", stream=True)
logger = loghelper.get_logger("crawler_screenshot")

#mongo
mongo = db.connect_mongo()
collection = mongo.info.website
imgfs = gridfs.GridFS(mongo.gridfs)

dest ="jpeg/"

# websites = [
#     {"_id": "576ca8144877af49c9dc7fad", "redirect_url": "http://www.51talkenglish.com"},
#     {"_id": "576ca8144877af49c9dc7fae", "redirect_url": "http://www.fxiaoke.com"},
#     {"_id": "576ca8144877af49c9dc7faf", "redirect_url": "http://stockradar.net"},
#     {"_id": "576ca8144877af49c9dc7fb0", "redirect_url": "http://www.91waijiao.com"},
#     {"_id": "576ca8144877af49c9dc7fb1", "redirect_url": "http://apps.renren.com/stockradar"},
#     {"_id": "576ca8144877af49c9dc7fb2", "redirect_url": "http://wangdian.cn"},
#     {"_id": "576ca8144877af49c9dc7fb3", "redirect_url": "http://www.zhaogang.com"},
#     {"_id": "576ca8144877af49c9dc7fb4", "redirect_url": "http://changba.com"},
#     {"_id": "576ca8144877af49c9dc7fb7", "redirect_url": "http://www.ibbd.net"},
#     {"_id": "576ca8144877af49c9dc7fb8", "rrm edirect_url": "http://www.wisemedia.cn"},
#     {"_id": "576ca8144877af49c9dc7fb9", "redirect_url": "http://www.hqrm.cn"},
#     {"_id": "576ca8144877af49c9dc7fba", "redirect_url": "http://www.qiyin.cn"}
# ]

class phantomjsScreenshot:
    def __init__(self):
        self.process = None

    def run(self, url, websiteId, dest, timeout):
        def target():
            #self.cmd = '/Users/mac/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs screenshot_phjs.js %s %s %s' % (url, websiteId, dest)
            self.cmd = '/opt/phantomjs/bin/phantomjs screenshot_phjs.js %s %s %s' % (url, websiteId, dest)
            logger.info(self.cmd)
            logger.info('Screenshot started')
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            stdout, stderr = self.process.communicate()
            logger.info(stdout)
            logger.info('Screenshot finished')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            logger.info('Terminating process')
            self.process.terminate()
            thread.join()
        logger.info("return code %s",self.process.returncode)


    def save(self, jpgfile, websiteId):
        img = open(jpgfile, 'rb')
        data = img.read()
        website_screen_id = imgfs.put(data, content_type='jpeg', filename='website_%s.jpg' % (websiteId))
        logger.info("Saved: %s", website_screen_id)
        if website_screen_id is not None:
            return website_screen_id
        else:
            return None



def start_run():
    crawler_screenshot = phantomjsScreenshot()
    while True:
        logger.info("website screenshot start...")

        websites = list(collection.find({"screenshotTime": None, "httpcode": 200}, limit=1000))
        for website in websites:
            url = website["redirect_url"]
            id = str(website["_id"])
            logger.info(url)
            start = datetime.datetime.now()
            crawler_screenshot.run(url, id, dest, timeout=30)
            end = datetime.datetime.now()
            logger.info("Time cost %s s",(end - start).seconds)

            screenshotId = None

            jpgfile = dest+id+'.jpg'
            if os.path.isfile(jpgfile):
                size = os.path.getsize(jpgfile)
                if size > 0:
                    screenshotId = crawler_screenshot.save(jpgfile, id)
                os.remove(jpgfile)

            screenshotTime = datetime.datetime.now()
            collection.update_one({"_id": website["_id"]}, {"$set": {"screenshotTime": screenshotTime, "screenshotId": screenshotId}})

        if len(websites) == 0:
            break

        #break
        logger.info("website screenshot end.")



if __name__ == "__main__":
    while True:
        start_run()
        # break   #test
        time.sleep(5 * 60)


