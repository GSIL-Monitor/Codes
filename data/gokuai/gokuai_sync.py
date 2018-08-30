# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import gokuaiapi

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config, name_helper

#logger
loghelper.init_logger("gokuai_sync", stream=True)
logger = loghelper.get_logger("gokuai_sync")


def get_lib_collection(org):
    mongo = db.connect_mongo()
    return mongo, mongo.gokuai["lib%s" % org["organizationId"]]


def get_file_collection(org):
    mongo = db.connect_mongo()
    return mongo, mongo.gokuai["file%s" % org["organizationId"]]


def get_deal_id(org_id, str):
    deal_id = None
    s = str.split("-")
    if len(s) > 1:
        try:
            deal_id = int(s[0].strip())
        except:
            pass
    if deal_id is not None:
        conn =  db.connect_torndb()
        deal = conn.get("select * from deal where id=%s and organizationId=%s", deal_id, org_id)
        conn.close()
        if deal is None:
            deal_id = None
    return deal_id


def update_libs(org):
    new_libs = gokuaiapi.getLibs(org["clientid"], org["clientsecret"])

    mongo, collection = get_lib_collection(org)
    old_libs = get_libs(org)

    # 增加新的lib
    for new_lib in new_libs:
        # patch mount_id
        collection.update({"org_id":new_lib["org_id"]}, {"$set":{"mount_id": new_lib["mount_id"]}})

        exist = False
        deal_id = get_deal_id(org["organizationId"], new_lib["org_name"])
        for old_lib in old_libs:
            if new_lib["org_id"] == old_lib["org_id"]:
                exist = True
                if new_lib["org_name"] != old_lib["org_name"]:
                    logger.info("update lib: %s -> %s", old_lib["org_name"], new_lib["org_name"])
                    collection.update_one({"_id":old_lib["_id"]},
                                      {"$set":{"org_name":new_lib["org_name"], "dealId":deal_id,
                                               "modifyTime": datetime.datetime.utcnow()}})
                break
        if exist is False:
            logger.info("new lib: %s", new_lib["org_name"])
            data = {
                "org_id": new_lib["org_id"],
                "org_name": new_lib["org_name"],
                "mount_id": new_lib["mount_id"],
                "org_client_id": None,
                "org_client_secret": None,
                "dealId": deal_id,
                "fetch_dateline": 0,
                "createTime": datetime.datetime.utcnow(),
                "modifyTime": datetime.datetime.utcnow(),
            }
            collection.insert_one(data)

    # 删除不存在的lib
    for old_lib in old_libs:
        exist = False
        for new_lib in new_libs:
            if new_lib["org_id"] == old_lib["org_id"]:
                exist = True
                break
        if exist is False:
            logger.info("remove lib: %s", old_lib["org_name"])
            collection.delete_one({"_id": old_lib["_id"]})
            mongo1, c_file = get_file_collection(org)
            c_file.delete_many({"lib_id": old_lib["_id"]})
            mongo1.close()


    # 无授权的获取授权
    libs = get_libs(org)
    for lib in libs:
        if lib["org_client_id"] is None or lib["org_client_secret"] is None:
            org_client_id, org_client_secret = gokuaiapi.getLibToken(org["clientid"], org["clientsecret"], lib["org_id"])
            collection.update_one({"_id":lib["_id"]},
                                      {"$set":{
                                          "org_client_id": org_client_id,
                                          "org_client_secret": org_client_secret
                                      }})
    mongo.close()


def get_libs(org):
    mongo, collection = get_lib_collection(org)
    libs = list(collection.find({}))
    mongo.close()
    return libs


def update_files(org, lib):
    if lib["dealId"] is None:
        return

    logger.info("get updated file list: %s", lib["org_name"])
    updates = []
    fetch_dateline = lib["fetch_dateline"]
    result = gokuaiapi.getUpdatedFileList(lib["org_client_id"], lib["org_client_secret"], fetch_dateline)
    while len(result["list"]) > 0:
        updates.extend(result["list"])
        fetch_dateline = result["fetch_dateline"]
        result = gokuaiapi.getUpdatedFileList(lib["org_client_id"], lib["org_client_secret"], fetch_dateline)

    updates.sort(lambda x, y: cmp(x["fullpath"], y["fullpath"]))

    mongo, collection = get_file_collection(org)
    for item in updates:
        # logger.info(item)
        if item["filename"] == "Thumbs.db":
            continue
        if item["filename"] == "__MACOSX":
            continue
        if item["filename"].startswith("."):
            continue

        (parentdir, basename) = os.path.split(item["fullpath"])

        logger.info("fullpath: %s, cmd: %s", item["fullpath"], item["cmd"])
        if item["cmd"] == 0:
            # delete
            collection.delete_one({"hash": item["hash"]})
        else:
            file = collection.find_one({"hash": item["hash"]})
            if file is not None:
                # update
                collection.update_one({"_id": file["_id"]}, {"$set":item})
            else:
                # new
                (parentdir, basename) = os.path.split(item["fullpath"])
                if parentdir == '':
                    # root
                    level = 1
                    parent_id = None
                else:
                    # child
                    parentdir = parentdir.rstrip('\\')
                    res = collection.find_one({"lib_id":str(lib["_id"]), "fullpath": parentdir, "dir": 1})
                    if res is None:
                        continue
                    parent_id = res["_id"]
                    level = res["level"] + 1
                item["lib_id"] = str(lib["_id"])
                if parent_id is None:
                    item["parent_id"] = None
                else:
                    item["parent_id"] = str(parent_id)
                item["level"] = level
                collection.insert_one(item)

    mongo1, c_lib = get_lib_collection(org)
    c_lib.update_one({"_id": lib["_id"]}, {"$set":{"fetch_dateline":fetch_dateline}})
    mongo1.close()

    mongo.close()

def process(org):
    logger.info("process orgId: %s", org["organizationId"])
    update_libs(org)
    libs = get_libs(org)
    for lib in libs:
        update_files(org, lib)
    logger.info("End orgId: %s", org["organizationId"])


def main():
    conn = db.connect_torndb()
    orgs = conn.query("select * from org_gokuai_conf where active='Y'")
    conn.close()
    for org in orgs:
        process(org)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(600)

