# -*- coding: utf-8 -*-
import os, sys
import datetime
import random
import json
import lxml.html
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer)

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import util

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)

#
company_collection = mongo.crawler_v2.company

sources = [13030, 13020]

if __name__ == "__main__":
    for source in sources:
        companies = company_collection.find({"source":source})
        for company in companies:
            company_key_int = int(company["company_key"])
            company_collection.update({"_id":company["_id"]},{"$set":{"company_key_int":company_key_int}})