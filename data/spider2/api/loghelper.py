#!/usr/bin/env python
# coding=utf-8
import os, sys
import datetime
import logging,traceback

reload(sys)
sys.setdefaultencoding("utf-8")


class GobiMessage:
    def __init__(self,gType,gValue):
        self.gType = gType
        self.gValue = gValue

    def __str__(self):
        return "type:%s, value:%s" % (self.gType,self.gValue)


class GobiHandler(logging.Handler):
    def __init__(self):
        #self.mongo = db.connect_mongo()
        #self.errorlog = self.mongo.log.errorlog
        logging.Handler.__init__(self)

    def emit(self, record):
        #print record.levelno
        #print "GobiHandler, %s" % self.clientName
        #print record.name

        if record.levelno < logging.ERROR:
            return

        if record.exc_info != None and record.exc_info != (None, None, None):
            (exc_type, exc_value, exc_traceback) = record.exc_info
            err_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            data = {"loggerName": record.name, "type":1, "value":err_msg, "date":datetime.datetime.utcnow()}
            #self.errorlog.insert_one(data)
        elif isinstance(record.msg, GobiMessage):
            #print "Find gobimessage!"
            data = {"loggerName": record.name, "type":record.msg.gType, "value":record.msg.gValue, "date":datetime.datetime.utcnow()}
            #self.errorlog.insert_one(data)
        elif isinstance(record.msg, basestring):
            data = {"loggerName": record.name, "type":2, "value":record.msg, "date":datetime.datetime.utcnow()}
            #self.errorlog.insert_one(data)
        else:
            data = {"loggerName": record.name, "type":3, "value":str(record.msg), "date":datetime.datetime.utcnow()}
            #self.errorlog.insert_one(data)


def handle_exception(exc_type, exc_value, exc_traceback, logger1):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    err_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    #print err_msg

    m = GobiMessage(0, err_msg)
    logger1.exception(m)

def init_logger(loggerName, stream=False):
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)  
    gobiHandler = GobiHandler()
    gobiHandler.setFormatter(formatter)
    logger.addHandler(gobiHandler)

    if stream:
        stream_handler = logging.StreamHandler()  
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler) 

    sys.excepthook = lambda exc_type, exc_value, exc_traceback,logger=logger:handle_exception(exc_type, exc_value, exc_traceback,logger)

def get_logger(loggerName):
    logger = logging.getLogger(loggerName)
    return logger

if __name__ == "__main__":
    init_logger("test1", stream=True)
    logger = get_logger("test1")
    logger.info('test')

    #type=0
    #raise RuntimeError("Test unhandled Exception2")

    #type=1
    try:
        raise RuntimeError("Test unhandled Exception")
    except Exception,ex:
        logger.exception(ex)
        pass


    #type=2
    #logger.error("test")

    #type=3
    #logger.error(Object("test"))
    
    #custome type
    #m = GobiMessage(4, "error1")
    #logger.error(m)

    

    

