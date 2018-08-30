# -*- coding: utf-8 -*-
import sys,os
import calendar
import datetime

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import db

#logger
loghelper.init_logger("card_prepare", stream=True)
logger = loghelper.get_logger("card_prepare")


def modify_date():
    Dates = []
    years = list(range(2007, 2010))
    months = list(range(1, 13))
    for year in years:
        for month in months:
            days = list(range(1, calendar.monthrange(year, month)[1] + 1))
            for day in days:
                date = "%d.%02d.%02d" % (year, month, day)
                Dates.append(date)
    # nians = list(range(2018,2019))
    # yues = list(range(1,7))
    # for nian in nians:
    #     for yue in yues:
    #         days = list(range(1, calendar.monthrange(nian, yue)[1] + 1))
    #         for day in days:
    #             if yue == 6 and day > 25:
    #                 continue
    #             date = "%d.%02d.%02d" % (nian, yue, day)
    #             Dates.append(date)
    # logger.info(Dates)
    return Dates

 #save to raw.qmp_dates
def save_dates(dates=None):
    if dates is None:
        dates = modify_date()
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_dates
    try:
        item = collection.find_one({'type':'date'})
        if item is not None:
            collection.delete_one({'type':'date'})
        collection_content = {
            'type':'date' ,
            'content': dates,
            'date': datetime.datetime.now()
        }
        collection.insert_one(collection_content)
        logger.info('save dates done')
    except:
        logger.info('mongo error')
    mongo.close()

def get_unionids():
    Unionids = []
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp
    try:
        items = collection.find({},{'postdata':1,'_id':0})
        for item in items:
            postdata = item['postdata']
            if postdata.has_key('unionid') and postdata['unionid'] is not None:
                unionid = postdata['unionid']
                if unionid  not in Unionids:
                    logger.info('a new:%s'%unionid)
                    Unionids.append(unionid)
    except:
        logger.info('mongo error')
    mongo.close()
    return Unionids

 # save to raw.qmp_id
def save_unionid(Unionids=None):
    if Unionids is None:
        Unionids = get_unionids()
    if Unionids is not None:
        for unionid in Unionids:
            mongo = db.connect_mongo()
            collection = mongo.raw.qmp_id
            try:
                item = collection.find_one({'unionid':unionid})
                if item is not None:
                    mongo.close()
                    continue
                collection_content = {
                    'type':'unionid',
                    'unionid':unionid,
                    'date':datetime.datetime.now(),
                    'active':1,
                    'used':0,
                    'inuse':0,
                    'proxy':'',
                    'daytimes':0,
                    'ondate':''
                }
                collection.insert_one(collection_content)
                logger.info('insert done:%s'%unionid)
            except:
                logger.info('mongo error')
            mongo.close()


if __name__ == '__main__':
    save_unionid()
    save_dates()

