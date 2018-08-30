# -*- coding: utf-8 -*-
__author__ = 'victor'

import sys
reload(sys)
sys.path.append('../..')
sys.path.append('../../nlp')
sys.setdefaultencoding('utf-8')

import logging
import os
import time
import json
import socket
import fcntl
import gridfs
from common import dbutil
from util import db as dbconfig
from util import config as config_settings
from common.dsutil import FixLenList
from pyvirtualdisplay import Display
from selenium import webdriver
from kafka import KafkaConsumer
from StringIO import StringIO
from PIL import Image


# logging
logging.getLogger('screen').handlers = []
logger_scr = logging.getLogger('screen')
logger_scr.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_scr.addHandler(stream_handler)


# image file system
imgfs = None

# kafka
consumer_shot = None

# picture size
shot_size = (0, 0, 1280, 800)

# browser controller
bc = None
browser = None


def init_mongodb():

    global logger_scr, imgfs
    try:
        client = dbconfig.connect_mongo()
        db = client.gridfs
        imgfs = gridfs.GridFS(db)
    except Exception, e:
        logger_scr.error('Mongodb connection error#%s' % e)


def init_kafka():

    global consumer_shot

    url = config_settings.get_kafka_config()
    consumer_shot = KafkaConsumer("aggregator", group_id="screen shot",
                                  metadata_broker_list=[url], auto_offset_reset='smallest')


def shot(br, url):

    global imgfs, shot_size
    if url.startswith('www'):
        url = 'http://%s' % url
    br.get(url)
    time.sleep(5)
    img = Image.open(StringIO(br.get_screenshot_as_png())).crop(shot_size)
    output = StringIO()
    img.save(output, format='jpeg')
    return imgfs.put(output.getvalue(), content_type='jpeg', filename='cover.jpg')


class BrowserController(object):

    def __init__(self, brs):

        self.brs = brs
        self.control = {}

    def get_avaliable_br(self):

        pid = os.getpid()
        if pid in self.control:
            return self.control.get(pid)
        else:
            br = self.brs.pop()
            self.control[pid] = br
            return self.control.get(pid)


def reload_browser(used, br):

    if used % 100 == 0:
        global logger_scr
        if br:
            br.get('https://www.baidu.com/')
            br.quit()
        br = webdriver.Firefox()
        br.set_window_size(1280, 800)
        logger_scr.info('Browser reset')
        __clear_brs()
    if not br:
        br = webdriver.Firefox()
        br.set_window_size(1280, 800)
        __clear_brs()
        logger_scr.info('Browser reset')
    return br


def __clear_brs():

    gcs = map(lambda y: str(y[1]),
              filter(lambda x: int(x[2]) == 1,
                     [line.split() for line in os.popen('ps -ef | grep firefox').readlines()]))
    if gcs:
        os.popen('kill %s' % ' '.join(gcs))

    gcs = map(lambda y: str(y[1]),
              filter(lambda x: int(x[2]) == 1,
                     [line.split() for line in os.popen('ps -ef | grep Xvfb').readlines()]))
    if gcs:
        os.popen('kill %s' % ' '.join(gcs))


def incremental_shotting(missing_only=True):

    global imgfs, consumer_shot, logger_scr, browser
    init_mongodb()
    init_kafka()
    display = Display(visible=0, size=(1280, 800))
    display.start()
    # browser = webdriver.Firefox()
    # browser.set_window_size(1280, 800)
    socket.setdefaulttimeout(60)
    recent = FixLenList(1000)

    while True:
        logger_scr.info('Start')
        try:
            for index, message in enumerate(consumer_shot):
                cid = json.loads(message.value).get('_id')
                try:
                    db = dbconfig.connect_torndb()
                    if missing_only and (not dbutil.miss_screen_shot(db, cid)):
                        logger_scr.info('%s#Had Done' % cid)
                    else:
                        locker = open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'screenshot.lock'))
                        fcntl.flock(locker, fcntl.LOCK_EX)
                        logger_scr.info('Incremental shotting gets the locker')
                        browser = reload_browser(index, browser)
                        process_1company(db, browser, cid, missing_only)
                        fcntl.flock(locker, fcntl.LOCK_UN)
                        locker.close()
                    consumer_shot.task_done(message)
                    consumer_shot.commit()
                    recent.append(cid)
                except Exception, e:
                    logger_scr.error(e)
                    logger_scr.error('non-br error # %s # %s' % (cid, e))
                finally:
                    # unlock and try to close database
                    try:
                        db.close()
                    except Exception, e:
                        pass
        except Exception, e:
            logger_scr.error('outside error#%s' % e)
            logger_scr.error(message)


def full_shotting(missing_only=True):

    global imgfs, consumer_shot, logger_scr, browser, bc

    init_mongodb()
    init_kafka()
    display = Display(visible=0, size=(1280, 800))
    display.start()
    # browser = webdriver.Firefox()
    # browser.set_window_size(1280, 800)
    mysql_db = dbconfig.connect_torndb()
    socket.setdefaulttimeout(60)

    locker = open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'screenshot.lock'))
    fcntl.flock(locker, fcntl.LOCK_EX)
    logger_scr.info('Full shotting got the locker')
    logger_scr.info(time.ctime())
    for index, cid in enumerate(sorted(dbutil.get_cids2shot(mysql_db), reverse=True)):
        browser = reload_browser(index, browser)
        process_1company(mysql_db, browser, cid, missing_only)
    fcntl.flock(locker, fcntl.LOCK_UN)
    locker.close()
    mysql_db.close()
    browser.quit()
    logger_scr.info('All done')


def shot_particular(*cids):

    global imgfs, browser
    init_mongodb()
    display = Display(visible=0, size=(1280, 800))
    display.start()
    browser = reload_browser(0, browser)
    mysql_db = dbconfig.connect_torndb()
    socket.setdefaulttimeout(100)
    for cid in cids:
        process_1company(mysql_db, browser, cid, False)
    mysql_db.close()
    browser.quit()
    display.__exit__()


def process_1company(mysql_db, br, cid, missing_only):

    global logger_scr
    try:
        missed_aids = dbutil.miss_screen_shot(mysql_db, cid)
        if missing_only and (not missed_aids):
            logger_scr.info('%s#Had Done' % cid)
            return True
        for missed_aid in missed_aids:
            website = dbutil.get_artifact_website(mysql_db, missed_aid)
            if website and valid_url(website):
                mongo_id = shot(br, website)
                dbutil.update_screenshot(mysql_db, missed_aid, mongo_id)
                logger_scr.info('process %s#company %s shot' % (os.getpid(), cid))
            else:
                logger_scr.info('process %s#company %s has no valid website' % (os.getpid(), cid))
            time.sleep(2)
        return True
    except socket.timeout:
        logger_scr.error('process %s#%s# time out' % (os.getpid(), cid))
        return False
    except Exception, e:
        logger_scr.info(e)
        logger_scr.error('process %s#%s#%s' % (os.getpid(), cid, e))
        return False


def valid_url(url):

    filter_keys = ['taobao', 'weibo']
    for key in filter_keys:
        if key in url:
            return False
    return True


if __name__ == '__main__':

    print __file__

    # full_shotting(missing_only=True)

    if sys.argv[1] == 'incr' or sys.argv[1] == 'incremental':
        # incrementally screen shot website
        incremental_shotting()
    elif sys.argv[1] == 'reshot' or sys.argv[1] == 'missing':
        # go through all websites, shot the ones without screen shot
        full_shotting(missing_only=True)
    elif sys.argv[1] == 'particular' or sys.argv[1] == 'part':
        shot_particular(*sys.argv[2:])
    else:
        full_shotting(missing_only=False)
