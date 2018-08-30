# -*- coding: utf-8 -*-
import  sys,os

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import db

def get_companyFullname_by_gongshang(investorName):
    mongo = db.connect_mongo()
    collection = mongo.info.gongshang
    results = list(collection.find({'$or' : [ {"investors.name":{'$regex':investorName}} ,{"changeInfo.contentAfter":{'$regex':investorName}} ]}))
    # results = list(collection.find({"investors.name":{'$regex':investorName}}))
    mongo.close()

    if len(results) > 0:
      return results
    else:
        return []

if __name__ == "__main__":
    pass
    # for i in get_companyFullname_by_gongshang('戈壁'):print i['name']