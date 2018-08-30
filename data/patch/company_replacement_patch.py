# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config, name_helper

#logger
loghelper.init_logger("company_replacement_patch", stream=True)
logger = loghelper.get_logger("company_replacement_patch")


def patch_task_news():
    mongo = db.connect_mongo()
    corporate_decompose_tasks = mongo.task.corporate_decompose.find({"processStatus":3})
    for task in corporate_decompose_tasks:
        logger.info(task)
        for replacement in task["replacement"]:
            replacement_company(replacement["oldCompanyId"], replacement["newCompanyId"])

    corporate_reaggregate_tasks = mongo.task.corporate_reaggregate.find({"processStatus":3})
    for task in corporate_reaggregate_tasks:
        logger.info(task)
        for replacement in task["replacement"]:
            replacement_company(replacement["oldCompanyId"], replacement["newCompanyId"])
    mongo.close()


def replacement_company(oldCompanyId, newCompanyId):
    mongo = db.connect_mongo()
    tasks = mongo.task.news.find({"companyIds": oldCompanyId})
    for task in tasks:
        mongo.task.news.update_one({"_id": task["_id"]}, {"$pull": {"companyIds": oldCompanyId}})
        mongo.task.news.update_one({"_id": task["_id"]}, {"$addToSet": {"companyIds": newCompanyId}})
    mongo.close()

if __name__ == "__main__":
    patch_task_news()

