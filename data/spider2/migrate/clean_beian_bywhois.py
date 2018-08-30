# -*- coding: utf-8 -*-
import os, sys
from pymongo import MongoClient
import pymongo
import time
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
reload(sys)

sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config
import db
import util


#logger
loghelper.init_logger("domain_2_beian", stream=True)
logger = loghelper.get_logger("domain_2_beian")

#mongo
mongo = db.connect_mongo()
collection = mongo.info.beian


BEIANS =[]

def whoisCheck():
    while True:
        if len(BEIANS) == 0:
            return
        beian = BEIANS.pop(0)

        #logger.info(beian["domain"])
        domain = str(beian["domain"])
        creation_date = util.whois_creation_date(domain)

        if creation_date is not None:
            logger.info("%s : %s -> %s", beian["domain"], beian["beianDate"], creation_date)
            if beian["beianDate"] > creation_date:
                collection.update({"domain": beian["domain"]}, {"$set": {"whoisChecked": True, "whoisExpire":"N"}},multi=True)
            else:
                logger.info("Expire %s", domain)
                collection.update({"domain": beian["domain"]}, {"$set": {"whoisChecked": True, "whoisExpire":"Y"}},multi=True)
        else:
            logger.info("%s has no whois data",domain)

            collection.update({"domain": beian["domain"]}, {"$set": {"whoisChecked": True, "whoisExpire":"NA"}},multi=True)


if __name__ == "__main__":
    concurrent_num = 30
    while True:
        logger.info("beian check by whois start...")
        # run(appmkt, WandoujiaCrawler(), "com.ctd.m3gd")
        beians = list(collection.find({"whoisChecked": {"$ne": True}}, limit=10000))
        for beian in beians:
            BEIANS.append(beian)

        #logger.info(BEIANS)

        if len(beians) > 0:
            threads = [gevent.spawn(whoisCheck) for i in xrange(concurrent_num)]
            gevent.joinall(threads)
        else:
            #break
            logger.info("beian check by whois end.")
            time.sleep(30 * 60)