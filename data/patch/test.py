# -*- coding: utf-8 -*-
import os, sys
import time
import pymongo

def main():
    mongo = pymongo.MongoClient()
    items = []
    try:
        item = mongo.xiniudata.entry.find_one({'path': '/api2/service/x_service/person_home/list_latest_funding_companies'}, max_time_ms=1000).test()
        print(item)
    except Exception as e:
        print(e)

    # for item in items:
    #     logger.info(item)

if __name__ == "__main__":
    main()